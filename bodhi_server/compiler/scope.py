import random
from devtools import debug
from typing import Any, Dict, List
from loguru import logger

from pydantic import Field

from bodhi_server import base_conf
from bodhi_server import FMod
from bodhi_server import rx
from bodhi_server.compiler import Flavor
from bodhi_server.compiler.utils import flexify
from bodhi_server import utils
from pydantic import root_validator

# type: ignore
class Scope(FMod):
    namespace: str
    flavor: Flavor
    defs: Dict[str, Any] = Field(default_factory=dict)
    uses: Dict[str, Any] = Field(default_factory=dict)

    @staticmethod
    def new(ns, flavor):
        return Scope(namespace=ns, flavor=flavor)  # type: ignore


# -----------------------------------------------------------------------------


def create_scope(ns, flavor):
    return Scope(namespace=ns, flavor=flavor)  # type: ignore


# -----------------------------------------------------------------------------
class Hierarchy(FMod):
    net: rx.PyDiGraph = rx.PyDiGraph()  # type: ignore
    prior_scope: int = 0
    curr_scope: int = 0
    scope_mapping: Dict[str, int] = dict()

    @property
    def scope(self) -> Scope:
        return self.net[self.curr_scope]

    @root_validator
    def init_scope(cls, values):
        node_idx = values["net"].add_node(create_scope("global", Flavor.GLOBAL))
        values["curr_scope"] = node_idx
        return values

    def add_scope(self, namespace: str, flavor: Flavor):
        # if not self.net.num_nodes():
        #     node_idx = self.net.add_node(Scope.new("global", Flavor.GLOBAL))
        #     self.latest_scope = node_idx
        #     return

        curr_idx = self.net.add_child(self.curr_scope, create_scope(namespace, flavor), {"relationship": "subscope"})  # type: ignore
        self.prior_scope = self.curr_scope
        self.curr_scope = curr_idx
        self.scope_mapping[namespace] = curr_idx
        return curr_idx

    def revert_scope(self):
        return self.parent()

    def set_scope(self, namespace: str):
        if namespace in self.scope_mapping:
            self.curr_scope = self.scope_mapping[namespace]
            return True
        elif namespace == "global":
            node_idx = self.net.add_node(create_scope("global", Flavor.GLOBAL))
            self.curr_scope = node_idx
        return False

    def parent(self):
        return self.direct_predecessors(self.curr_scope)

    def parents(self):
        return self.net.predecessors(self.curr_scope)

    def direct_successors(self, node_id):
        """
        Direct successors id of a given node as sorted list.
        Args:
            node_id (int): label of considered node.
        Returns:
            List: direct successors id as a sorted list
        """
        return sorted(list(self.net.adj_direction(node_id, False).keys()))

    def direct_predecessors(self, node_id):
        """
        Direct predecessors id of a given node as sorted list.
        Args:
            node_id (int): label of considered node.
        Returns:
            List: direct predecessors id as a sorted list
        """
        return sorted(list(self.net.adj_direction(node_id, True).keys()))

    def get_node(self, namespace: str):
        if namespace in self.scope_mapping:
            return self.net[self.get_id(namespace)]
        try:
            if namespace == "global":
                return self.net[0]
        except Exception as e:
            raise AttributeError("Scope not found")

    def get_id(self, namespace: str):
        if namespace in self.scope_mapping:
            return self.scope_mapping[namespace]
        raise AttributeError("Scope not found")

    def node_count(self) -> int:
        return self.net.num_nodes()

    def define(self, name, expr_id: int):
        self.scope.defs[name] = expr_id

    def assign(self, name, expr_id: int):
        self.scope.defs[name] = expr_id

    def access(self, name):
        return self.scope.defs[name]


class NamespaceLink(FMod):
    defs: Dict[str, List[str]] = Field(default_factory=dict)
    uses: Dict[str, List[str]] = Field(default_factory=dict)

    def sort_defs(self, name: str, scope_map: Dict[str, int]):
        map_idxs = list(
            map(lambda x: {"name": name, "idx": scope_map[x]}, self.defs[name])
        )
        print(map_idxs)

        sorted_map = sorted(map_idxs, key=lambda x: x["idx"])
        return list(reversed(sorted_map))


class ScopeConroller(FMod):
    # The heirarchy of various namespaces. Cah use for parents
    scope_graph: Hierarchy = Hierarchy()
    depth: int = 0  # The call depth we're currently at.
    # The name spaces where delcarations have been made for a given symbol.
    # We use this to determine if a symbol is within any scope before  going further.
    names: NamespaceLink = NamespaceLink()
    ns_history: List[str] = []

    @property
    def namespace(self):
        """The namespace property."""

        return self.ns_history[-1] if self.ns_history else "global"

    @property
    def scope(self) -> Scope:
        """The namespace property."""

        return self.curr_scope()

    def set_scope(self, namespace: str, flavor: Flavor):
        self.depth += 1
        self.ns_history.append(namespace)
        return self.scope_graph.add_scope(namespace, flavor)

    def end_scope(self):
        self.depth -= 1
        self.scope_graph.set_scope(self.revert_history())
        # debug(self.sc_hier.parents())

    def revert_history(self):
        return self.ns_history.pop() if self.ns_history else "global"

    def get_name(self):
        return self.namespace

    def curr_scope(self) -> Scope:
        return self.get_scope(self.namespace)

    def get_scope(self, namespace: str):
        return self.scope_graph.get_node(namespace)

    def is_defined(self, symbol: str) -> bool:
        if symbol not in self.names.defs or self.names.defs[symbol] == []:
            return False
        return True

    def is_defined_local(self, symbol: str) -> bool:
        local_list = self.names.defs.get(symbol, [])
        if self.namespace in local_list:
            return True
        return False

    def _def_symbol(self, symbol: str, expr_id: int):
        def_namespaces = self.names.defs.get(symbol, [])
        self.names.defs[symbol] = list(set([self.namespace] + def_namespaces))
        self.scope_graph.define(symbol, expr_id)

    def define(self, symbol: str, expr_id: int):
        if not self.is_defined(symbol) or not self.is_defined_local(symbol):
            self._def_symbol(symbol, expr_id)
            return True

            # self.names.defs[symbol].append(ns)
            # self.scope_graph.assign(symbol, expr_id)
        raise RuntimeError("Undefined variable")

    def assign(self, symbol: str, expr_id: int):
        if self.is_defined(symbol):
            if self.is_defined_local(symbol):
                self.is_defined_local(symbol)

            self.scope_graph.define(symbol, expr_id)
        else:
            raise RuntimeError("Undefined variable")

    # def access(self, symbol: str):
    #     if not self.is_defined(symbol):
    #         raise RuntimeError("Variable not defined anywhere")

    #     for ns in self.names.sort_defs(symbol):
    #         pass

    def momentum(self):
        debug(self.scope_graph.parents())
        # self.names.sort_defs("momentum", self.scope_graph.scope_mapping)

    def access_local(self, symbol: str):
        for ns in self.names.defs[symbol]:
            if ns == self.namespace:
                return self.scope_graph.access(symbol)

    def draw_scope(self):
        utils.graphviz_show(
            self.scope_graph.net, node_attr_fn=lambda x: {"label": x.namespace}
        )

    # CommonConfig


@logger.catch
def main():
    def count_set():
        count = 0

        def _get_count():
            nonlocal count
            count += random.randint(1, 10)
            return count

        return _get_count

    sc = ScopeConroller()
    counter = count_set()
    sc.set_scope("cowcheese", Flavor.METHOD)
    sc.define("momentum", counter())
    sc.set_scope("blue_cheese", Flavor.BLOCK)
    sc.momentum()
    sc.define("momentum", counter())
    sc.set_scope("pydantic", Flavor.IMPORTEDITEM)
    sc.define("momentum", counter())

    sc.momentum()
    # debug(sc.curr_scope())
    sc.end_scope()
    sc.end_scope()
    sc.end_scope()
    sc.end_scope()
    sc.end_scope()
    sc.end_scope()
    sc.end_scope()
    sc.end_scope()
    sc.end_scope()
    # debug(sc.curr_scope())
    sc.define("x", counter())
    sc.define("love", counter())
    sc.define("buy", counter())
    sc.set_scope("lover", Flavor.METHOD)
    sc.define("momentum", counter())
    # debug(sc.curr_scope())
    sc.draw_scope()

    # logger.info(scope_control.get_scope())


if __name__ == "__main__":
    main()
