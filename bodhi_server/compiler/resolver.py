from typing import Union

from loguru import logger

import bodhi_server.compiler.circuit.decompiler as inter
from bodhi_server.compiler.callables import *
from bodhi_server.compiler.operations import *
from bodhi_server.compiler import Visitor


class Resolver(Visitor):
    interpreter = inter.Interpreter
    scopes: List[Dict[str, bool]] = field(default_factory=[])

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

    def resolve(self, stmt: Union[Stmt, Expr]):
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

    def resolve_local(self, expr: Expr, name: Token):
        for idx, item in enumerate(reversed(self.scopes)):
            if name.lexeme in item:
                self.interpreter.resolve(expr, idx)
                return

    def visit_assign_expr(self, expr: Assign):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_function_stmt(self, stmt: Function):
        self.declare(stmt.name)
        self.define(stmt.name)

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
