import abc
import time
from datetime import datetime
from pathlib import Path
from typing import Any, cast, Dict, List, Optional, Union

from devtools import debug
from loguru import logger

import retworkx as rx
from pydantic import Field
from pydantic import root_validator
from rich import print

from bodhi_server import FlexModel
from bodhi_server import utils
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

# from bodhi_server.compiler.callables import Clock
from bodhi_server.compiler.bodhi_ir import edges as ex
from bodhi_server.compiler.bodhi_ir import nodes as dx
from bodhi_server.compiler.bodhi_ir.abc import IREdge
from bodhi_server.compiler.bodhi_ir.abc import IRNode
from bodhi_server.compiler.bodhi_ir.abc import IRVisitor
from bodhi_server.compiler.bodhi_ir.visitors.json_convert import JsonVisitor
from bodhi_server.compiler.env import Environment
from bodhi_server.compiler.operations import Assign
from bodhi_server.compiler.operations import Block
from bodhi_server.compiler.operations import Break
from bodhi_server.compiler.operations import Continue
from bodhi_server.compiler.operations import ExprStmt
from bodhi_server.compiler.operations import Function
from bodhi_server.compiler.operations import If
from bodhi_server.compiler.operations import Module
from bodhi_server.compiler.operations import Print
from bodhi_server.compiler.operations import Return
from bodhi_server.compiler.operations import Var
from bodhi_server.compiler.operations import While
from bodhi_server.compiler.utils import flexify


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
        lexeme = node.token.lexeme
        operation = dx.get_binary(lexeme)()
        binop_idx = self.ast.add_node(operation)  # type: ignore

        self.ast.add_edge(binop_idx, self.visit(node.right), ex.Right())
        self.ast.add_edge(binop_idx, self.visit(node.right), ex.Left())

        # logger.info("Running binary")
        # debug(operation)
        return binop_idx

    def visit_unary(self, node: Unary):
        lexeme = node.token.lexeme
        operation = dx.get_unary(lexeme)()
        unary_idx = self.ast.add_node(operation)  # type: ignore

        self.ast.add_edge(unary_idx, self.visit(node.expr), ex.Expr())
        return unary_idx

    def visit_grouping(self, node: Grouping):
        unary_idx = self.ast.add_node(dx.Group())  # type: ignore

        self.ast.add_edge(unary_idx, self.visit(node.expr), ex.GroupIn())
        return unary_idx

    def visit_literal(self, node: Literal):
        val = node.value
        val_node = self.ast.add_node(dx.get_literal(type(val))(value=val))  # type: ignore
        return val_node

    def visit_module(self, expr: Module):
        module_idx = self.ast.add_node(dx.Module())  # type: ignore
        for idx, body_stmt in enumerate(expr.body):
            self.ast.add_edge(module_idx, self.visit(body_stmt), ex.StmtOf(index=idx))
        return module_idx

    def visit_variable_expr(self, expr: Expr):
        raise NotImplementedError

    def visit_assign_expr(self, expr: Expr):
        raise NotImplementedError

    def visit_logical_expr(self, expr: Expr):
        raise NotImplementedError

    def visit_call_expr(self, expr: Expr):
        raise NotImplementedError


class __IRAnalyzer(__IRAnalyzer):  # type: ignore
    def visit_expression_stmt(self, stmt: ExprStmt):  # type: ignore
        # debug(self.ast)
        expr_stmt_idx = self.ast.add_node(dx.ExprStmt())
        self.ast.add_edge(expr_stmt_idx, self.visit(stmt.expr), ex.Expr())
        return expr_stmt_idx

    def visit_expr_stmt(self, stmt: ExprStmt):
        return self.visit_expression_stmt(stmt)

    def visit_block_stmt(self, stmt: Stmt):
        raise NotImplementedError

    def add_conditional(self, stmt: IRNode, condition: Expr) -> int:
        stmt_idx = self.ast.add_node(stmt)
        self.ast.add_edge(stmt_idx, self.visit(condition))
        return stmt_idx

    def visit_if_stmt(self, stmt: If):  # type: ignore
        if_idx = self.add_conditional(dx.If(), stmt.condition)
        self.ast.add_edge(if_idx, self.visit(stmt.then_branch), ex.IsTrue())
        self.ast.add_edge(if_idx, self.visit(stmt.else_branch), ex.IsFalse())
        return if_idx

    def visit_while_stmt(self, stmt: While):  # type: ignore
        while_idx = self.add_conditional(dx.While(), stmt.condition)
        self.ast.add_edge(while_idx, self.visit(stmt.body), ex.IsTrue())
        return while_idx

    def visit_block(self, stmt: Block):
        block_idx: int = self.ast.add_node(dx.Block())
        for idx, body_stmt in enumerate(stmt.stmts):
            self.ast.add_edge(block_idx, self.visit(body_stmt), ex.StmtOf(index=idx))
        return block_idx

    def visit_function_stmt(self, stmt: Function):  # type: ignore
        # We're giving a function a name
        func_idx = self.ast.add_node(dx.Function(identity=stmt.name.lexeme))
        if stmt.params is not None:
            for param in stmt.params:
                self.ast.add_child(
                    func_idx, dx.Param(identity=param.lexeme), ex.Param()
                )
        self.ast.add_edge(func_idx, self.visit(stmt.body), ex.Body())

        return func_idx

    def visit_return_stmt(self, stmt: Stmt):
        raise NotImplementedError

    def visit_return_module(self, expr: Module):
        raise NotImplementedError

    def analyze(self, stmts: Union[List[Stmt], Stmt]):
        if not isinstance(stmts, list):
            stmts = [stmts]
        # logger.warning(stmts)
        self.environment = Environment()
        for stmt in stmts:
            self.visit(stmt)

    def to_dict(self):
        """Convert convert the graph into a dictionary."""
        pass


class IRAnalyzer(__IRAnalyzer):
    """Statement managment"""

    pass


def node_display(node: IRNode):
    label_str = f"{node.name}"
    if node.is_value:
        label_str = f"{label_str}:{node.value}"

    return {"label": label_str, "shape": "box"}


def edge_display(node: IREdge):
    label_str = f"{node.name}"
    # response = {"label": f"{node.name}:{node.identity}"}
    # name = node.name
    color = "black"
    if "true" in node.name or "right" in node.name:
        color = "green"
    if "false" in node.name or "left" in node.name:
        color = "blue"
    return {"color": color}


@logger.catch
def run(stmts: Union[List[Stmt], Stmt]) -> rx.PyDAG:
    """Run the IR analyzer on the source code."""
    from bodhi_server.compiler.resolver import Resolver

    if not isinstance(stmts, list):
        stmts = [stmts]
    analyzer = IRAnalyzer()  # type: ignore

    analyzer.analyze(stmts)  # type: ignore
    ast_graph = analyzer.ast
    # utils.graphviz_show(ast_graph, node_attr_fn=node_display, edge_attr_fn=edge_display)
    return ast_graph


def main():
    from bodhi_server.compiler import operations as opx

    logger.info("Starting the interpreter")
    analyzer = IRAnalyzer()

    fnx = Module(
        body=[
            opx.fn_stmt(
                "hello",
                opx.block(
                    [
                        opx.expr_stmt(
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
    graph = run([fnx])
    debug(graph.edges())

    visitor = JsonVisitor(graph)
    result = visitor.start()
    debug(result)
    # decomps = rx.dag_longest_path(graph)
    # debug(decomps)

    # for node in graph.nodes():
    #     print(node.to_dict())
    # analyzer.analyze([fnx])
    # print(analyzer.ast.nodes())
    # nested_scopes = "var hello = 1234.456;"
    # Note: The scanner has a index bug. Will need to solve it at some point.
    # nested_scopes = " 10 * 12 + ( 1 + 1 ) "
    pass

    # resp = interp.intepret(parsed_stmts)
    # print(resp)


if __name__ == "__main__":
    main()
