import abc
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from loguru import logger
from rich import print

from mangostar.compiler import (
    Binary,
    Grouping,
    Literal,
    Node,
    Token,
    TokenType,
    Unary,
    Visitor,
)
from pydantic import Field
from mangostar import FMo
from mangostar.compiler.callables import *
from mangostar.compiler import ICallable
from mangostar.compiler.env import Environment
from mangostar.compiler.operations import *

CWD_DIR = Path.cwd()


@dataclass
class __Interpreter(FModel, Visitor):  # type: ignore
    environment: Optional[Environment] = None
    globals: Environment = Environment()
    locals: Dict[Expr, int] = {}  # type: ignore

    @property
    def env(self):
        """The env property."""
        if self.environment is None:
            raise AttributeError("Environment is not defined.")
        return self.environment

    @env.setter
    def env(self, value: Environment):
        self._env = Environment

    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth
        return

    def look_up_variable(self, name: Token, expr: Expr):
        distance = self.locals.get(expr, None)
        if distance is not None:
            return self.env.get_at(distance, name.lexeme)
        return self.globals.access(name)

    def __post_init__(self):
        self.globals.define("clock", Clock())
        self.environment = self.globals

    def is_truthy(self, value: Any) -> bool:
        if value is None:
            return False

        if isinstance(value, bool):
            return value

        return True

    def is_equal(self, first: Any, second: Any) -> bool:
        return first == second


class __Interpreter(__Interpreter):
    def visit_binary(self, expr: "Binary"):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        token_type = expr.token.token_type

        if token_type == TokenType.GREATER:
            return float(left) > float(right)
        elif token_type == TokenType.GREATER_EQUAL:
            return float(left) >= float(right)
        elif token_type == TokenType.LESS:
            return float(left) < float(right)
        elif token_type == TokenType.LESS_EQUAL:
            return float(left) <= float(right)
        elif token_type == TokenType.BANG_EQUAL:
            return self.is_equal(left, right)
        elif token_type == TokenType.MINUS:
            return float(left) - float(right)
        elif token_type == TokenType.SLASH:
            return float(left) / float(right)
        elif token_type == TokenType.STAR:
            return float(left) * float(right)
        elif token_type == TokenType.PLUS:
            if isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)
            elif isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return float(left) + float(right)
            raise TypeError("One of the two evaluated expressions is off.")

    def visit_unary(self, node: "Unary"):
        right = self.evaluate(node.expr)
        exp_types = {
            TokenType.MINUS: lambda x: (-1 * x),
            TokenType.BANG: lambda x: (not self.is_truthy(x)),
        }
        resp_fn = exp_types.get(node.token.token_type, None)
        if resp_fn is not None:
            return resp_fn(right)
        raise Exception("Shouldn't have touched this here.")

    """
        Normal expressions 
    """

    def visit_grouping(self, expr: "Grouping") -> str:
        return self.evaluate(expr.expr)

    def visit_literal(self, node: "Literal") -> Any:
        return node.value

    def visit_token(self, node: "Token"):
        logger.debug("Visiting a token")

    def visit_expression_stmt(self, stmt: ExprStmt):
        return self.evaluate(stmt.expr)

    def visit_print(self, print_stmt: Print):
        value = self.evaluate(print_stmt.expr)
        print(str(value))

    def evaluate(self, node: "Node") -> Any:
        return self.visit(node)


class Interpreter(__Interpreter):
    """Statement managment"""

    def visit_var_stmt(self, stmt: "Var"):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)

        self.env.define(stmt.name.lexeme, value)

    def visit_variable_expr(self, expr: Variable) -> Any:
        return self.environment.get(expr.name)

    def visit_assign_expr(self, expr: Assign):
        value = self.evaluate(expr.value)
        distance = self.locals.get(expr, None)
        if distance:
            self.env.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)

        return value

    def visit_block_stmt(self, stmt: Block) -> None:
        self.execute_block(stmt.stmts, Environment(enclosing=self.environment))

    def visit_if_stmt(self, stmt: If):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.evaluate(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.evaluate(stmt.else_branch)

    def visit_logical_expr(self, expr: Binary):
        """
        The concept is a bit complex. Though we're saying the following rules:

        1. if the statement is an OR statement, and the first is true, the conditions are met. Skip the next check.
        2. If the statement is and AND statement, and the first condition is true.
            1. Then you must check the second condition because both must be true.
            2. Otherwise, if the first condition is false, skip it. All of it is false then.

        Args:
            expr (Binary): This the comparison statement overall.

        Returns:
            bool: Hopefully returns a boolean type.
        """
        left = self.evaluate(expr.left)
        if expr.token.token_type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        return self.evaluate(expr.right)

    def visit_while_stmt(self, stmt: Stmt):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_call_expr(self, expr: Call):
        callee = self.evaluate(expr.callee)

        args = []
        for arg in expr.arguments:
            args.append(self.evaluate(arg))
        if not isinstance(expr.paren, ABCCallable):
            raise RuntimeError("Can only call functions and classes")

        func = cast(ABCCallable, callee)
        size = func.arity()
        arg_count = len(args)
        if arg_count != size:
            raise RuntimeError(f"expected {size} arguments but got {arg_count}")

        return func.call(self, *args)

    def visit_function_stmt(self, stmt: Function):
        function: DubFunction = DubFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)

    def visit_return_stmt(self, stmt: Stmt):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise ReturnErr(value)

    #

    def execute_block(self, stmts: List[Stmt], environment: Environment):
        previous = self.env
        try:
            self.env = environment

            for stmt in stmts:
                self.evaluate(stmt)
        except Exception as e:
            raise e
        finally:
            self.env = previous

    def intepret(self, stmts: List[Stmt]):

        try:
            for stmt in stmts:
                self.evaluate(stmt)
        except Exception as e:
            raise e


def main():
    # nested_scopes = "var hello = 1234.456;"
    # Note: The scanner has a index bug. Will need to solve it at some point.
    # nested_scopes = " 10 * 12 + ( 1 + 1 ) "
    pass

    # resp = interp.intepret(parsed_stmts)
    # print(resp)


if __name__ == "__main__":
    main()
