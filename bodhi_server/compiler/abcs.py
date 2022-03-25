import abc
from abc import ABC
from typing import Any, AnyStr, List, Optional

from inflection import underscore
from loguru import logger

import retworkx as rx
from auto_all import end_all
from auto_all import start_all

from bodhi_server import FlexModel
from bodhi_server.compiler import Expr
from bodhi_server.compiler import Stmt
from bodhi_server.compiler.types import TokenType


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


class ParentDetails(FlexModel, ABC):
    """Parent Node Details"""

    conn_type: Optional[TokenType] = None
    index: int = -1

    @property
    def is_parent(self):
        """The is_ property."""
        return self.index > -1


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


class Node(FlexModel, abc.ABC):
    node_decomposer: Optional[INodeDecomp] = None

    @property
    def cls_name(self) -> str:
        return underscore(type(self).__name__).lower()

    @property
    def node_name(self) -> str:
        return underscore(type(self).__name__).lower()

    @property
    def vname(self) -> str:
        return f"visit_{self.cls_name}"

    @property
    def ltag(self) -> str:
        return f"leave_{self.cls_name}"

    def visit(self, visitor: "Visitor"):
        visitor.visit(self)

    def decompose(self, env: IASTGraph):
        if isinstance(self, Token):
            raise TypeError(
                f"The node {self.node_name} is a Token. It cannot be decomposed."
            )

        if not self.node_decomposer:
            raise AttributeError("The node_decomposer is not set.")
        self.node_decomposer.env = env
        return self.node_decomposer.decompose(self)


class StmtVisitor(abc.ABC):
    @abc.abstractmethod
    def visit_expression_stmt(self, stmt: Expr):
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
    def visit_binary(self, expr: Expr):
        raise NotImplementedError

    @abc.abstractmethod
    def visit_unary(self, node: Expr):
        raise NotImplementedError

    @abc.abstractmethod
    def visit_grouping(self, expr: Expr):
        raise NotImplementedError

    @abc.abstractmethod
    def visit_literal(self, expr: Expr):
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

    def visit(self, node: "Node"):
        """Allow the visitor run through multiple steps. Only"""

        return self.on_visit(node)

    def on_visit(self, node: Node):
        vname = node.vname
        visit_func = getattr(self, vname, None)

        is_function = visit_func is not None
        if not is_function:
            raise Exception(f"The function {vname} doesn't exist.")
        return_value = visit_func(node)
        return return_value


class Token(Node):
    token_type: TokenType
    lexeme: str
    literal: Optional[Any] = None
    line: Optional[int] = None

    def __str__(self) -> str:
        return f"Token(type={self.token_type}, lexeme={self.lexeme}, literal={self.literal})"


class PrintVisitor(Visitor):
    def on_visit(self, node: Node):
        logger.warning(f"Printing {node.vname}")
        super().on_visit(node)

    def visit_token(self, node: "Node"):
        logger.debug("Visiting a token")


end_all(globals())


def main():
    nand_token = Token(token_type=TokenType.AND, lexeme="and", literal="and", line=1)
    print_visit = PrintVisitor()
    print_visit.visit(nand_token)


if __name__ == "__main__":
    main()
