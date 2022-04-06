import abc
from abc import ABC
from typing import Any, AnyStr, Callable, List, Optional, Union

from inflection import underscore
from loguru import logger

import retworkx as rx
from auto_all import end_all
from auto_all import start_all

from bodhi_server import FlexModel
from bodhi_server import utils
from bodhi_server.compiler import BinopType
from bodhi_server.compiler import NodeType
from bodhi_server.compiler import OpType
from bodhi_server.compiler import TokenType
from bodhi_server.compiler import UnaryType
from bodhi_server.compiler.types import TokenType


AstType = Union[TokenType, UnaryType, BinopType, NodeType, OpType, None]

start_all(globals())


class IASTGraph(ABC):
    @abc.abstractproperty
    def graph(self) -> rx.PyDiGraph:  # type: ignore
        raise NotImplementedError()


class ICallable(FlexModel, ABC):
    @abc.abstractmethod
    def arity(self) -> int:
        pass

    @abc.abstractmethod
    def call(self, inter: "Any", *args):
        pass


# class ParentDetails(FlexModel, ABC):
#     """Parent Node Details"""

#     conn_type: Optional[TokenType] = None
#     index: int = -1

#     @property
#     def is_parent(self):
#         """The is_ property."""
#         return self.index > -1


class INodeDecomp(ABC):
    @property
    def env(self) -> IASTGraph:
        """The graph property."""
        return self._env

    @env.setter
    def env(self, value: IASTGraph):
        self._env = value

    @abc.abstractmethod
    def decompose(self, node: "Node"):
        pass


class INode(ABC):
    pass


class IStmt(ABC):
    pass


class IExpr(ABC):
    pass


class IToken(ABC):
    pass


class ILiteral(ABC):
    pass


class Node(FlexModel, INode, abc.ABC):
    # node_decomposer: Optional[INodeDecomp] = None

    @property
    def cls_name(self) -> str:
        return underscore(type(self).__name__).lower()

    @property
    def node_name(self) -> str:
        return underscore(type(self).__name__).lower()

    @property
    def visit_name(self) -> str:
        return f"visit_{self.cls_name}"

    @property
    def leave_tag(self) -> str:
        return f"leave_{self.cls_name}"

    def visit(self, visitor: "Visitor"):
        visitor.visit(self)


class Token(Node, IToken):
    token_type: AstType
    lexeme: str
    literal: Optional[Any] = None
    line: Optional[int] = None

    def __str__(self) -> str:
        return f"Token(type={self.token_type}, lexeme={self.lexeme}, literal={self.literal})"


class Expr(Node, IExpr):
    """An expression can be anything."""

    pass


class Stmt(Node, IStmt, ABC):
    """A statement inside of the internal programming language"""

    pass


class Binary(Expr):
    left: Expr
    right: Expr
    token: Token


class Grouping(Expr):
    expr: Expr


class Literal(Expr, ILiteral):
    value: Any


class Unary(Expr):
    expr: Expr
    token: Token


class StmtVisitor(abc.ABC):
    @abc.abstractmethod
    def visit_expression_stmt(self, stmt: Union["Expr", "Stmt", None]):
        raise NotImplementedError

    @abc.abstractmethod
    def visit_block_stmt(self, stmt: Stmt):
        raise NotImplementedError

    @abc.abstractmethod
    def visit_if_stmt(self, stmt: Stmt):
        raise NotImplementedError

    @abc.abstractmethod
    def visit_while_stmt(self, stmt: Stmt):
        raise NotImplementedError

    @abc.abstractmethod
    def visit_function_stmt(self, stmt: Stmt):
        raise NotImplementedError

    @abc.abstractmethod
    def visit_return_stmt(self, stmt: Stmt):
        raise NotImplementedError


class ExprVisitor(abc.ABC):
    @abc.abstractmethod
    def visit_binary(self, expr: Binary):
        raise NotImplementedError

    @abc.abstractmethod
    def visit_unary(self, node: Unary):
        raise NotImplementedError

    @abc.abstractmethod
    def visit_grouping(self, expr: Grouping):
        raise NotImplementedError

    @abc.abstractmethod
    def visit_literal(self, expr: Literal):
        raise NotImplementedError

    @abc.abstractmethod
    def visit_variable_expr(self, expr: Expr):
        raise NotImplementedError

    @abc.abstractmethod
    def visit_assign_expr(self, expr: Expr):
        raise NotImplementedError

    @abc.abstractmethod
    def visit_logical_expr(self, expr: Expr):
        raise NotImplementedError

    @abc.abstractmethod
    def visit_call_expr(self, expr: Expr):
        raise NotImplementedError


class Visitor(FlexModel, abc.ABC):
    """
    The Visitor Interface declares a set of visiting methods that correspond to
    component classes. The signature of a visiting method allows the visitor to
    identify the exact class of the component that it's dealing with.
    """

    @abc.abstractmethod
    def instance_visit(self, node: Node) -> Optional[Any]:

        raise NotImplementedError(
            "To avoid rewritting code, use this method to visit parent visitors."
        )

    def visit(self, node: "Node"):
        """Allow the visitor run through multiple steps. Only"""

        return self.on_visit(node)

    def get_visit_func(self, name: str) -> Callable:
        """Get the visit function for the given name."""

        def vname(_str: str):
            return f"{name}_{_str}"

        return (
            getattr(self, name, None)
            or getattr(self, vname("stmt"), None)
            or getattr(self, vname("expr"), None)
        )

    def on_visit(self, node: Node):
        visit_name = node.visit_name
        inst_visit = self.instance_visit(node)
        if inst_visit is not None:
            return inst_visit

        visit_func = self.get_visit_func(visit_name)

        is_function = visit_func is not None
        if not is_function:
            raise Exception(f"The function {visit_name} doesn't exist.")
        return_value = visit_func(node)
        return return_value


class PrintVisitor(Visitor):
    def on_visit(self, node: Node):
        logger.warning(f"Printing {node.visit_name}")
        super().on_visit(node)

    def visit_token(self, node: "Node"):
        logger.debug("Visiting a token")

    def instance_visit(self, node: Node) -> Optional[Any]:
        return super().instance_visit(node)


end_all(globals())


def main():
    nand_token = Token(token_type=TokenType.AND, lexeme="and", literal="and", line=1)
    print_visit = PrintVisitor()
    print_visit.visit(nand_token)


if __name__ == "__main__":
    main()
