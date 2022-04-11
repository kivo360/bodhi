import abc
from abc import ABC
from functools import cache, cached_property
from typing import Any, Dict, Optional, Type, Union

import retworkx as rx

from bodhi_server import FlexModel
from bodhi_server import utils
from bodhi_server.compiler import BinopType
from bodhi_server.compiler import EdgeTypes
from bodhi_server.compiler import NodeType
from bodhi_server.compiler import Token
from bodhi_server.compiler import TokenType
from bodhi_server.compiler import UnaryType
from bodhi_server.compiler.types import AstType
from loguru import logger
from toolz import valfilter, keyfilter


class IRComponent(ABC):
    pass


class IRConverter(ABC):
    def convert(self, node: Any) -> Any:
        raise NotImplementedError()


class IREdge(IRComponent, FlexModel, ABC):
    type: EdgeTypes

    @property
    def name(self) -> str:
        return utils.consistent_naming(self.__class__.__name__)

    def compute_dot(self) -> dict:
        return {}
        # if self.has_token:
        #     return f"{self.type.name} {self.value}"
        # return self.name


class IRNodeConvert(IRConverter, ABC):
    def convert(self, node: "IRNode") -> Dict[str, Any]:
        node_resp = {"type": node.read_name}

        return node_resp


class IRNode(IRComponent, FlexModel, ABC):
    name: str = utils.hexid()
    value: Optional[Any] = None
    type: AstType = None
    convert: IRNodeConvert = IRNodeConvert()

    @property
    def has_token(self) -> bool:
        return self.type is not None

    @property
    def is_value(self) -> bool:
        return self.value is not None

    @property
    def read_name(self) -> str:
        return utils.consistent_naming(self.name)

    def compute_dot(self) -> dict:
        return {}

    def to_dict(self) -> dict:
        return self.convert.convert(self)


def edge_filter(node_map: Dict[int, IREdge], check_type: Type) -> Dict[int, IREdge]:
    return valfilter(lambda x: isinstance(x, check_type), node_map)


class IAccessNode(abc.ABC):
    """A class that represents a node in the IR graph. It's used to access key attributes related to a given node."""

    @abc.abstractproperty
    def current(self) -> IRNode:
        pass

    @abc.abstractproperty
    def type(self):
        # The type of the node
        pass

    @abc.abstractmethod
    def parents(self):
        pass

    @abc.abstractmethod
    def children(self):
        pass

    @abc.abstractmethod
    def successors(self):
        pass

    @abc.abstractmethod
    def ancestors(self):
        pass

    @abc.abstractmethod
    def target(self):
        pass

    @abc.abstractmethod
    def statements(self):
        pass

    @abc.abstractmethod
    def left(self):
        pass

    @abc.abstractmethod
    def right(self):
        pass

    @abc.abstractmethod
    def value(self):
        pass

    @abc.abstractmethod
    def children_edge(self, edge_type: Type) -> Dict[int, IREdge]:
        pass


class IValidator(abc.ABC):
    def __init__(self, acc_node: IAccessNode) -> None:
        self.node = acc_node

    def is_binary(self):
        pass

    def is_body(self):
        pass
        # follow = self.acc_node.children()
        # print(follow.values())


class AccessNode(IAccessNode):
    """A class that represents a node in the IR graph. It's used to access key attributes related to a given node."""

    def __init__(
        self,
        node_id: int,
        graph: rx.PyDiGraph,
        validator_type: Optional[Type[IValidator]] = None,
    ) -> None:
        self.graph = graph
        self.node_id = node_id
        self._validator_type: Optional[Type[IValidator]] = validator_type

    @property
    def current(self) -> IRNode:
        return self.graph[self.node_id]

    @cached_property
    def type(self):
        # The type of the node
        return type(self.current)

    @property
    def validator_type(self):
        """The validator_type property."""
        return self._validator_type

    @validator_type.setter
    def validator_type(self, value):
        self._validator_type = value

    def parents(self):
        pass

    @cache
    def children(self) -> Dict[int, IREdge]:
        # logger.warning(list(self.successors()))
        return keyfilter(lambda x: x in self.successors(), self.graph.adj(self.node_id))

    @cache
    def successors(self) -> Dict[int, IREdge]:
        return self.graph.successor_indices(self.node_id)

    def children_edge(self, edge_type: Type) -> Dict[int, IREdge]:
        return edge_filter(self.children(), edge_type)

    def ancestors(self):
        return IRNode()

    def target(self):
        return self.graph[self.node_id]

    def statements(self):
        return IRNode()

    def left(self):
        return IRNode()

    def right(self):
        return IRNode()

    def value(self):
        return IRNode()

    def initialize(self):
        self.validator = self.validator_type(self)
        return self


class IRVisitor(ABC):
    def __init__(self, graph: rx.PyDiGraph) -> None:
        super().__init__()
        self.current_idx = 0
        self.graph = graph
        self._validator = None

    @cached_property
    def first(self):
        for node_index in rx.topological_sort(self.graph):
            return node_index
        raise IndexError("No nodes in graph")

    @property
    def current(self) -> IRNode:
        return self.get_node(self.index)

    @property
    def index(self) -> int:
        return self.current_idx

    @index.setter
    def index(self, value: int):
        self.current_idx = value

    @property
    def validator(self):
        """The validator property."""
        return self._validator

    @validator.setter
    def validator(self, value):
        self._validator = value

    def get_node(self, node_id: int, is_set: bool = False) -> IRNode:
        if is_set:
            self.index = node_id
        return self.graph[node_id]

    def to_access(self):
        if self.validator is None:
            raise ValueError("Validator not set")
        access = AccessNode(self.current_idx, self.graph)
        access.validator_type = self.validator
        return access.initialize()

    def visit(self, node: IRNode) -> Any:
        return self.on_visit(node)

    def on_visit(self, node: IRNode) -> Any:
        visit_fn_name = f"visit_{node.read_name}"
        visit_fn = getattr(self, visit_fn_name, None)
        if visit_fn is None:
            logger.warning(f"No visitor for node {node.read_name}")
            raise NotImplementedError(f"No visitor for node: {node.read_name}")
        return visit_fn(self.to_access())
        # logger.info(self.first)
        # logger.info(visit_fn_name)
        # logger.info(visit_fn)

    def start(self):
        self.current_idx = self.first
        return self.visit(self.current)
