"""This has all of the core operations. We base everything else off of these operations."""
import abc
from ast import Dict
from dataclasses import field
from datetime import datetime
from pathlib import Path
from typing import Any, List

from auto_all import end_all, start_all
from pydantic import Field

from mangostar.compiler import TokenType
from mangostar.compiler import Token
from mangostar.compiler import (
    Stmt,
    Expr,
    Unary,
    Binary,
    Grouping,
    Literal,
)  # isort:skip

CWD_DIR = Path.cwd()

start_all(globals())


class ExprStmt(Stmt):
    expr: Expr


class Print(ExprStmt):
    pass


class Var(Stmt):
    name: Token
    initializer: Expr


class Variable(Stmt):
    """
    A way to access the variables. Commonly bound to a class or function.
    """

    name: Token


class Assign(Stmt):
    """
    A way to access the variables.

    Args:
        Stmt ([type]): [description]
    """

    name: Token
    value: Expr


class Block(Stmt):
    stmts: List[Stmt] = Field([])


class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt


class While(Stmt):
    condition: Expr
    body: Stmt


class Call(Stmt):
    callee: Expr
    paren: Token
    arguments: List[Expr] = Field([])


class Return(Stmt):
    keyword: Token
    value: Expr


class Logical(Expr):
    left: Expr
    right: Expr
    token: Token


class ReturnErr(RuntimeError):
    def __init__(self, value: Any, *args: object) -> None:
        super().__init__(*args)
        self.value = value


end_all(globals())


#
# class Callable(Stmt):
#     callee: Expr
#     paren: Token
#     arguments: Expr


if __name__ == "__main__":
    test_binary = Binary(
        right=Unary(Literal(123), token=Token(TokenType.MINUS, "-", None, 1)),
        token=Token(TokenType.STAR, "*", None, 1),
        left=Grouping(Literal(45.67)),
    )

    print(test_binary)
