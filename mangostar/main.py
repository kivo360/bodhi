import abc
import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from inflection import camelize
from inflection import tableize
from inflection import underscore
from loguru import logger

import addict as adt
import more_itertools as mtoolz
import networkx as nx
import orjson
import stringcase
import typer

from mangostar.pytables import *
from mangostar.utils import *

SYS_MAP = DynamicGlobalMap()


@lru_cache
def make_cache(node_json: str):
    return hashlib.md5(node_json).hexdigest()


class Node(abc.ABC):
    def __init__(
        self,
        node_type: str,
        name: Optional[str] = None,
        is_entity: bool = False,
        sub_type: Optional[str] = None,
        **attrs
    ):
        self._node_type: str = node_type
        # Value represents a, Optionalnything important that we need to regularly access
        self._value: Any = None
        self._parent: Union['Node'] = None
        self._is_entity = is_entity
        self._name = name
        self._sub_type = sub_type
        self._attrs = attrs

    @property
    def name(self) -> str:
        """The name of the node combined with a second hash.

        Returns:
            str: Returns the name of a hash.
        """
        useful_name: str = self.__class__.__name__
        if self._name is not None:
            useful_name = self._name
        return underscore(useful_name)

    @property
    def node_id(self) -> str:
        """Get the unique identifier for this node .

        Returns:
            str: An id that has the format: {name}-{node_hash}
        """
        return f"{self.name}-{self.node_hash}"

    @property
    def props(self) -> dict:
        return self._attrs

    @property
    def is_entity(self):
        return self._is_entity

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, _parent: 'Node'):
        self._parent = _parent

    @property
    def graph_repr(self) -> adt.Dict:
        graph_repr = adt.Dict()
        graph_repr.name = self.name
        graph_repr.attrs = adt.Dict(**self._attrs)
        graph_repr.attrs.node_type = self.ntype
        if self._sub_type is not None:
            graph_repr.attrs.sub_type = self._sub_type
        if self.value:
            graph_repr.attrs.node_value = self.value
        return graph_repr

    @property
    def graph_repr_dict(self) -> Dict:
        return self.graph_repr.to_dict()

    @property
    def node_hash(self) -> str:
        local_rep = deepcopy(self.graph_repr)
        local_rep.pop("name", None)
        node_json = orjson.dumps(
            local_rep.to_dict(), option = orjson.OPT_SORT_KEYS
        )
        return make_cache(node_json)

    @property
    def ntype(self) -> str:
        return underscore(self._node_type).lower()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, _value):
        self._value = _value

    def add_props(self, **attrs):
        self._attrs.update(attrs)

    def __repr__(self) -> str:
        return f"{camelize(self.ntype)}({self.name}, parent={self.parent})"

    @abc.abstractmethod
    def add(self, node: 'Node'):
        raise NotImplementedError


class System(Node):
    def __init__(self):
        super().__init__("system", is_entity = False)
        self.value = nx.DiGraph(name = self.name)

    @property
    def net(self) -> nx.DiGraph:
        return self.value

    @property
    def node_count(self) -> int:
        return self.net.number_of_nodes()

    @property
    def edge_count(self) -> int:
        return self.net.number_of_edges()

    @property
    def root_id(self) -> str:
        if self.node_count > 0:
            return self.net.graph.get("root_id", None)
        raise ValueError("there hasn't been an added root yet")

    def extract_id(self, node: Union['Subsystem', str]) -> str:
        if isinstance(node, Subsystem):
            return node.node_id
        elif isinstance(node, str):
            return node
        else:
            raise TypeError("Unsupported node type supplied")

    def get_node(self, node: Union['Subsystem', str]):
        """Get the node view of a given node

        Args:
            node (Union[): THe node that we're searching for.

        Returns:
            nx.NodeView: The node that we're asking for.
        """
        return self.net.nodes[self.extract_id(node)]

    def successors(
        self,
        node: Union['Subsystem', str],
        depth_limit: int = 1,
        protocol: Literal['breadth', 'depth'] = "breadth"
    ):
        """Return the successors of a node .

        Args:
            node (Union[Subsystem, str]): The subsystem or node we're looking for. 
            depth_limit (int, optional): The default depth. Defaults to 1.
            protocol (Literal[, optional): The protocol we're looking for. Defaults to "breadth".

        Returns:
            dict: A dictionary of relationships.
        """
        if protocol == "breadth":
            return dict(
                nx.bfs_successors(self.net, node, depth_limit = depth_limit)
            )
        return dict(
            nx.dfs_successors(self.net, node, depth_limit = depth_limit)
        )

    def add_node(self, node: 'Subsystem'):
        if self.node_count == 0:
            self.net.graph.update({"root_id": node.node_id})
        self.net.add_node(node.node_id, **node.graph_repr_dict)

    def add_edge(self, parent: 'Subsystem', child: 'Subsystem', **edges):
        self.net.add_edge(parent.node_id, child.node_id, **edges)

    def add(self, node: 'Subsystem', **edges):
        node.system = self
        self.add_node(node)
        if node.parent:
            self.add_edge(node.parent, node, **edges)

    def to_dict(self):
        return json.loads(nx.jit_data(self.net))


class Subsystem(Node):
    def __init__(
        self,
        _node_type: str,
        name: Optional[str] = None,
        is_entity: bool = False,
        sub_type: Optional[str] = None,
        **attrs
    ):
        super().__init__(
            _node_type,
            name = name,
            is_entity = is_entity,
            sub_type = sub_type,
            **attrs
        )

    def add_current(self, _sys: Optional[System] = None):
        """Add the current entity to the system .

        Args:
            _sys (Optional[System, optional): We'll set this variable if the system we're adding to is different from the default. Defaults to None.
        """
        if _sys:
            self.system = _sys
        self.system.add(self)

    @property
    def system(self) -> System:
        if not self._system:
            self.system = system()
        return self._system

    @system.setter
    def system(self, _system: System) -> None:
        self._system = _system

    def add(self, node: 'Subsystem', **edge_props: dict):
        node.parent = self
        node.system = self.system
        self.system.add(node, **edge_props)
        return node


class Entity(Subsystem):
    def __init__(
        self,
        sub_type: Optional[str] = None,
        name: Optional[str] = None,
        node_type: Optional[str] = None,
        **attrs
    ):
        entity_type = sub_type or node_type or self.name
        super().__init__(
            "entity",
            is_entity = True,
            name = name,
            sub_type = tableize(entity_type),
            **attrs
        )

    @property
    def name(self) -> str:
        if self._name is not None:
            return tableize(self._name)
        return tableize(self.__class__.__name__)


class Component(Subsystem):
    def __init__(
        self,
        _type: Optional[str] = "component",
        name: Optional[str] = None,
        sub_type: Optional[str] = None,
        **attrs
    ):
        super().__init__(
            "component",
            is_entity = False,
            sub_type = _type,
            name = name,
            **attrs
        )


class SystemProperties:
    def __init__(self, _system: System):
        self._system: System = _system

    @property
    def system(self) -> System:
        return self._system

    @system.setter
    def system(self, _system: System) -> System:
        self._system = _system

    @property
    def num_nodes(self) -> int:
        return self.system.node_count

    @property
    def num_edges(self) -> int:
        return self.system.edge_count

    @property
    def is_dag(self) -> bool:
        return nx.is_directed_acyclic_graph(self.system.net)

    @property
    def root_id(self) -> str:
        return self.system.root_id

    @property
    def is_root(self) -> bool:
        return bool(self.root_id)

    @property
    def top_sorted(self) -> List[str]:
        """Topological sort of the network .

        Returns:
            List[str]: A list of ids with a topological sort.
        """
        return list(nx.topological_sort(self.system.net))

    @property
    def rev_top_sort(self) -> List[str]:
        """Returns a reversed topologically sorted network.

        Returns:
            List[str]: A revrsed topoloigcal sort
        """
        return list(reversed(self.top_sorted))


class Visitor(SystemProperties, abc.ABC):
    def __init__(self, _system: System):
        super().__init__(_system)
        self._current_step: int = 0
        self._current_nodes = {}
        # Prior Analyzed Nodes

    @property
    def has_started(self) -> bool:
        return self._current_step > 0

    @property
    def has_children(self) -> bool:
        """Checks the current nodes to detect if any of them has any children

        Should be run with `step_successors` prior.

        Returns:
            bool: False if none of the current nodes have children.
        """
        if not self.current_nodes:
            return False
        nodes: Dict[str, List[str]] = self.current_nodes
        is_children: bool = False
        for children in nodes.values():
            if not children:
                continue
            is_children = True
        return is_children

    @property
    def current_nodes(self) -> Dict[str, List[str]]:
        """Return the current nodes in the container .

        Returns:
            Dict[str, List[str]]: In the traversal step.
        """
        # If no movement set the system
        if not self.has_started:
            if not self.is_root:
                raise AttributeError("Root doesn't exist")
            self._current_nodes = {self.root_id: []}

        return self._current_nodes

    @property
    def num_parents(self) -> int:
        return len(self._current_nodes.keys())

    @property
    def num_children(self) -> int:
        return len(self.flat_children)

    @property
    def flat_children(self) -> List[str]:
        return list(mtoolz.flatten(self._current_nodes.values()))

    @logger.catch
    def step_successors(self, inf_depth: bool = False):
        nodes: Dict[str, List[str]] = self.current_nodes
        agg_nodes: dict = {}
        depth = 1 if not inf_depth else None
        n_keys = nodes.keys()
        for node in n_keys:
            succs: dict = self.system.successors(node, depth_limit = depth)
            temp = {
                **succs,
                **agg_nodes,
            }
            agg_nodes = temp
        self._current_nodes = agg_nodes

        return agg_nodes

    def update_switch(self):
        """Convert the childrent to the parents if there are any.
        """
        if self.has_children:
            self._current_nodes = {k: [] for k in self.flat_children}

    def increment(self) -> None:
        self._current_step += 1

    def label_multi_step(self) -> None:
        raise NotImplementedError

    def step(self):
        """
            Returns the next step in the depth succession algorithm. Will inherit this function to edit functionality.
        """
        self.step_successors(inf_depth = True)
        self.increment()

    @abc.abstractmethod
    def visit(self):
        raise NotImplementedError


def system(name: str = "default") -> System:
    if name in SYS_MAP:
        return SYS_MAP[name]

    SYS_MAP[name] = System()
    return SYS_MAP.get(name)


def snake(name: str):
    return stringcase.snakecase(name)


def add_path(current_path, *additions):
    path_set = [current_path] + list(additions)
    return Path(*path_set)


def main():
    sql_path = Path('sql')
    create_path = add_path(
        sql_path,
        "create",
    )
    create_path.mkdir(parents = True, exist_ok = True)
    # write_path
    for tb in TBList:
        typer.echo()
        with add_path(create_path, f"{tb.name}.sql").open(mode = "w") as f:
            s = crt_tbl(tb)
            f.write(str(s))
        typer.echo(s)


if __name__ == "__main__":
    typer.run(main)
