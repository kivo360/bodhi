"""This has all of the core operations. We base everything else off of these operations."""
from pathlib import Path
from typing import Any, List, Optional, Union

from auto_all import end_all, start_all
from pydantic import Field

from bodhi_server.compiler import Token
from bodhi_server.compiler import (
    Stmt,
    Expr,
    Unary,
    Binary,
    Grouping,
    Literal,
    ExprVisitor,
    StmtVisitor,
)
from bodhi_server.compiler.types import TokenType  # isort:skip

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


class Assign(Expr):
    """
    A way to access the variables.

    Args:
        Stmt ([type]): [description]
    """

    name: Token
    value: Expr

    # def accept(self, visitor: ExprVisitor):
    #     return visitor.visit_assign(self)


class Module(Stmt):
    body: List[Stmt] = []


class Block(Stmt):
    stmts: List[Stmt] = []


class Conditional(Stmt):
    condition: Expr


class If(Conditional):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt


class While(Conditional):
    condition: Expr
    body: Stmt


class For(Stmt):
    target: Expr
    iter: Expr
    body: Block
    orelse: Optional[Block] = None


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


class Function(Stmt):
    name: Token
    body: Block
    params: List[Token] = []

    def get_name(self):
        return self.name.node_name


class Break(Stmt):
    pass


class Continue(Stmt):
    pass


class String(Literal):
    value: str


class Integer(Literal):
    value: int


class Float(Literal):
    value: float


class ReturnErr(RuntimeError):
    def __init__(self, value: Any, *args: object) -> None:
        super().__init__(*args)
        self.value = value


def varname(name: str) -> Token:
    return Token(token_type=TokenType.IDENTIFIER, lexeme=name)


def string(value: str) -> String:
    return String(value=value)


def integer(value: int) -> Integer:
    return Integer(value=value)


def float_lt(value: float) -> Float:
    return Float(value=value)


def expr_stmt(expr: Expr) -> ExprStmt:
    return ExprStmt(expr=expr)


def print_stmt(expr: Expr) -> Print:
    return Print(expr=expr)


def var(name: str, initial: Expr) -> Var:
    return Var(name=varname(name), initializer=initial)


def variable(name: str) -> Variable:
    return Variable(name=varname(name))


def assign(name: str, val: Expr) -> Assign:
    return Assign(name=varname(name), value=val)


def block(stmts: List[Stmt]) -> Block:
    return Block(stmts=stmts)


def if_stmt(cond: Expr, then: Stmt, else_: Stmt) -> If:
    return If(condition=cond, then_branch=then, else_branch=else_)


def while_stmt(cond: Expr, body: Stmt) -> While:
    return While(condition=cond, body=body)


def for_stmt(target: Expr, iter: Expr, body: Block, orelse: Optional[Block]) -> For:
    return For(target=target, iter=iter, body=body, orelse=orelse)


def call_stmt(callee: Expr, paren: Token, arguments: List[Expr]) -> Call:
    return Call(callee=callee, paren=paren, arguments=arguments)


def return_stmt(kwd: Token, value: Expr) -> Return:
    return Return(keyword=kwd, value=value)


def fn_stmt(name: str, body: Block, params: List[Token]) -> Function:
    return Function(name=varname(name), body=body, params=params)


end_all(globals())


#


if __name__ == "__main__":
    pass
    # test_binary = Binary(
    # right=Unary(Literal(123), token=Token(TokenType.MINUS, "-", None, 1)),
    # token=Token(TokenType.STAR, "*", None, 1),
    # left=Grouping(Literal(45.67)),
    # )
#
# print(test_binary)
