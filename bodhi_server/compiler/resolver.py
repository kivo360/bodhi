from loguru import logger
from bodhi_server.compiler import scope

import bodhi_server.compiler.bodhi_ir.core as inter
from bodhi_server.compiler import *
from bodhi_server.compiler.callables import *
from bodhi_server.compiler.operations import *
from bodhi_server.compiler.utils import is_lit, is_binary, is_unary
from bodhi_server import utils
from devtools import debug

from typing import Union, List, Optional, Any, Dict, cast


class Resolver(Visitor):
    interpreter: inter.IRAnalyzer
    scopes: List[Dict[str, bool]] = []

    @property
    def scope_len(self):
        return len(self.scopes)

    def latest_scope(self):
        return self.scopes[-1] if not self.is_empty else None

    def is_empty(self):
        return self.scope_len == 0

    def visit_block_stmt(self, stmt: Block):
        self.begin_scope()
        # self.declare(stmt.)

        self.resolve_list(stmt.stmts)
        self.end_scope()
        return

    def resolve_list(self, statements: List[Stmt]):
        for statement in statements:
            self.resolve(statement)

    def resolve(self, stmts: Union[List[Stmt], List[Expr], Stmt, Expr]):
        stmts = utils.listify(stmts)
        for stmt in stmts:
            self.visit(stmt)

    def begin_scope(self):

        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if len(self.scopes) == 0:
            return
        self.scopes[-1][name.lexeme] = False

    def define(self, name: Token):
        if self.is_empty():
            return
        self.scopes[-1][name.lexeme] = True

    def visit_var_stmt(self, stmt: Var):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    def visit_variable_expr(self, expr: Variable):
        if not self.is_empty() and self.scopes[-1][expr.name.lexeme] == False:
            logger.error(expr.name)
            return
        self.resolve_local(expr, expr.name)

    def resolve_local(self, expr: Union[Expr, Stmt], name: Token):
        for idx, item in enumerate(reversed(self.scopes)):
            if name.lexeme in item:
                self.interpreter.resolve(expr=expr, depth=idx)  # type: ignore
                return

    def visit_assign_expr(self, expr: Assign):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_function_stmt(self, stmt: Function):
        self.declare(stmt.name)
        self.define(stmt.name)
        debug(stmt)
        self.resolve_function(stmt)

    def resolve_function(self, func: Function) -> None:
        self.begin_scope()
        for param in func.params:
            self.declare(param)
            self.define(param)

        self.resolve(func.body)
        self.end_scope()

    def visit_expression_stmt(self, stmt: ExprStmt):
        self.resolve(stmt.expr)

    def visit_if_stmt(self, stmt: If):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch:
            self.resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print):
        self.resolve(stmt.expr)

    def visit_return_stmt(self, stmt: Return):
        if stmt.value:
            self.resolve(stmt.value)

    def visit_while_stmt(self, stmt: While):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visit_binary(self, expr: Binary):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_call_expr(self, expr: Call):
        self.resolve(expr.callee)
        for argument in expr.arguments:
            self.resolve(argument)

    def visit_grouping_expr(self, expr: Grouping):
        self.resolve(expr.expr)

    def visit_literal_expr(self, expr: Literal):
        pass

    def visit_logical_expr(self, expr: Logical):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_unary_expr(self, expr: Unary):
        self.resolve(expr.expr)

    def resolve_stmts(self, statements: List[Stmt]):
        for statement in statements:
            self.resolve(statement)

    def instance_visit(self, node: Node):
        if is_binary(node):
            self.visit_binary(cast(Binary, node))
            return True
        if is_lit(node):
            self.visit_literal_expr(cast(Literal, node))
            return True

    def visit_expr_stmt(self, stmt: ExprStmt):
        self.resolve(stmt.expr)

    def visit_module(self, module: Module):
        self.resolve_stmts(module.body)
