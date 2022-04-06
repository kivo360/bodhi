import abc
import time
from datetime import datetime
from pathlib import Path
from typing import Any, cast, Dict, List, Optional, Union

from devtools import debug
from loguru import logger

import retworkx as rx
from pydantic import Field, root_validator
from rich import print

from bodhi_server import FlexModel
from bodhi_server.compiler import Binary
from bodhi_server.compiler import Expr
from bodhi_server.compiler import ExprVisitor
from bodhi_server.compiler import Grouping
from bodhi_server.compiler import ICallable
from bodhi_server.compiler import Literal
from bodhi_server.compiler import Node
from bodhi_server.compiler import Stmt
from bodhi_server.compiler import StmtVisitor
from bodhi_server.compiler import Token
from bodhi_server.compiler import TokenType
from bodhi_server.compiler import Unary
from bodhi_server.compiler import Visitor
from bodhi_server.compiler.utils import flexify

# from bodhi_server.compiler.callables import Clock
from bodhi_server.compiler.bodhi_ir import edges as ex
from bodhi_server.compiler.bodhi_ir import nodes as dx
from bodhi_server.compiler.bodhi_ir.abc import ASTNode
from bodhi_server.compiler.env import Environment
from bodhi_server.compiler.operations import Assign
from bodhi_server.compiler.operations import Block
from bodhi_server.compiler.operations import Break
from bodhi_server.compiler.operations import Continue
from bodhi_server.compiler.operations import ExprStmt
from bodhi_server.compiler.operations import Function
from bodhi_server.compiler.operations import If
from bodhi_server.compiler.operations import Print
from bodhi_server.compiler.operations import Return, Var
from bodhi_server.compiler.operations import While, Module

# from bodhi_server.compiler.operations import *


# from typing import Any, Union, cast, Dict, List, Optional


CWD_DIR = Path.cwd()


class __IRAnalyzer(Visitor, ExprVisitor, StmtVisitor):  # type: ignore
    globals: Environment = Environment()
    environment: Optional[Environment] = None
    locals: Dict[Expr, int] = dict()  # type: ignore

    input_map: Dict[str, str] = dict()
    output_map: Dict[str, str] = dict()
    op_nodes: Dict[str, str] = dict()

    internal_ast: rx.PyDAG = rx.PyDAG()

    def instance_visit(self, node: Node) -> Optional[Any]:
        if isinstance(node, Literal):
            return self.visit_literal(node)
        elif isinstance(node, Unary):
            return self.visit_unary(node)
        elif isinstance(node, Binary):
            return self.visit_binary(node)
        else:
            return None

    @property
    def ast(self) -> rx.PyDAG:
        """The env property."""
        if self.internal_ast is None:
            raise AttributeError("AST Graph not defined")
        return self.internal_ast

    @property
    def env(self):
        """The env property."""
        if self.environment is None:
            raise AttributeError("Environment is not defined.")
        return self.environment

    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth  # type: ignore

    def look_up_variable(self, name: Token, expr: Expr):
        distance = self.locals.get(expr, None)  # type: ignore
        if distance is not None:
            return self.env.get_at(distance, name.lexeme)
        return self.globals.access(name)

    def __post_init__(self):
        # self.globals.define("clock", Clock())
        self.environment = self.globals

    def is_truthy(self, value: Any) -> bool:
        if value is None:
            return False

        if isinstance(value, bool):
            return value

        return True

    def is_equal(self, first: Any, second: Any) -> bool:
        return first == second


class __IRAnalyzer(__IRAnalyzer):  # type: ignore
    def visit_binary(self, node: Binary):

        binop_idx = self.ast.add_node(dx.Binary(name=node.token.lexeme, type=node.token.token_type))  # type: ignore
        # right_node = node.right.decompose(self.env)
        # left_node = node.left.decompose(self.env)

        self.ast.add_edge(binop_idx, self.visit(node.right), ex.Right())
        self.ast.add_edge(binop_idx, self.visit(node.right), ex.Left())

        logger.info("Running binary")
        return binop_idx

    def visit_unary(self, node: Unary):
        unary_idx = self.ast.add_node(dx.Unary(name=node.token.lexeme, type=node.token.token_type))  # type: ignore

        self.ast.add_edge(unary_idx, self.visit(node.expr), ex.Expr())
        return unary_idx

    def visit_grouping(self, node: Grouping):
        unary_idx = self.ast.add_node(dx.Group())  # type: ignore

        self.ast.add_edge(unary_idx, self.visit(node.expr), ex.GroupIn())
        return unary_idx

    def visit_literal(self, node: Literal):
        val_node = self.ast.add_node(dx.Value(value=node.value))
        return val_node

    def visit_module(self, expr: Module):
        for stmt in expr.body:
            self.visit(stmt)

    def visit_variable_expr(self, expr: Expr):
        raise NotImplementedError

    def visit_assign_expr(self, expr: Expr):
        raise NotImplementedError

    def visit_logical_expr(self, expr: Expr):
        raise NotImplementedError

    def visit_call_expr(self, expr: Expr):
        raise NotImplementedError


class __IRAnalyzer(__IRAnalyzer):
    def visit_expression_stmt(self, stmt: ExprStmt):
        stmt_node = self.ast.add_node(dx.ExprStmt())
        self.ast.add_edge(stmt_node, self.visit(stmt.expr), ex.Expr())
        return None

    def visit_block_stmt(self, stmt: Stmt):
        raise NotImplementedError

    def add_conditional(self, stmt: ASTNode, condition: Expr) -> int:
        stmt_idx = self.ast.add_node(stmt)
        self.ast.add_edge(stmt_idx, self.visit(condition))
        return stmt_idx

    def visit_if_stmt(self, stmt: If):
        if_idx = self.add_conditional(dx.If(), stmt.condition)
        self.ast.add_edge(if_idx, self.visit(stmt.then_branch), ex.IsTrue())
        self.ast.add_edge(if_idx, self.visit(stmt.else_branch), ex.IsFalse())
        return if_idx

    def visit_while_stmt(self, stmt: While):
        while_idx = self.add_conditional(dx.While(), stmt.condition)
        self.ast.add_edge(while_idx, self.visit(stmt.body), ex.IsTrue())
        return while_idx

    def visit_function_stmt(self, stmt: Function):
        # We're giving a function a name
        self.env.define(stmt.name.lexeme, stmt)  # It's sort of doing what I need it to.
        debug(self.env)

    def visit_return_stmt(self, stmt: Stmt):
        raise NotImplementedError

    # def execute_block(self, stmts: List[Stmt], environment: Environment):
    #     previous = self.env
    #     try:
    #         self.env = environment

    #         for stmt in stmts:
    #             self.visit(stmt)
    #     except Exception as e:
    #         raise e
    #     finally:
    #         self.env = previous

    def analyze(self, stmts: Union[List[Stmt], Stmt]):
        if not isinstance(stmts, list):
            stmts = [stmts]

        self.environment = Environment()
        for stmt in stmts:
            self.visit(stmt)


class IRAnalyzer(__IRAnalyzer):
    """Statement managment"""

    pass


@logger.catch
def run(stmts: Union[List[Stmt], Stmt]) -> rx.PyDAG:
    """Run the IR analyzer on the source code."""
    from bodhi_server.compiler.resolver import Resolver

    if not isinstance(stmts, list):
        stmts = [stmts]
    analyzer = IRAnalyzer()
    resolver = Resolver(interpreter=analyzer)
    resolver.resolve_stmts(stmts)
    analyzer.analyze(stmts)
    # debug(resolver)
    return analyzer.ast


def main():
    from bodhi_server.compiler import operations as opx

    logger.info("Starting the interpreter")
    # analyzer = IRAnalyzer()

    fnx = Module(
        body=[
            opx.fn_stmt(
                "hello",
                opx.block(
                    [
                        ExprStmt(
                            expr=opx.add(
                                left=opx.float_lt(2),
                                right=opx.float_lt(2),
                            )
                        )
                    ]
                ),
                [],
            )
        ]
    )
    # debug(fnx)
    run([fnx])
    # analyzer.analyze([fnx])
    # nested_scopes = "var hello = 1234.456;"
    # Note: The scanner has a index bug. Will need to solve it at some point.
    # nested_scopes = " 10 * 12 + ( 1 + 1 ) "
    pass

    # resp = interp.intepret(parsed_stmts)
    # print(resp)


if __name__ == "__main__":
    main()
