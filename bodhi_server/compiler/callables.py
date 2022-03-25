import time
from typing import Any, List, Optional

from auto_all import end_all, start_all


from .interpreter import Interpreter
from .abcs import ICallable
from .env import Environment
from .operations import *

from bodhi_server.compiler import (
    Token,
    TokenType,
    Stmt,
    Expr,
    Unary,
    Binary,
    Grouping,
    Literal,
)

start_all(globals())


from dataclasses import dataclass, field  # isort:skip


class Clock(ICallable):
    def arity(self) -> int:
        return 0

    def call(self, inter: "Interpreter", args: List[Any]) -> float:
        return time.time() / 1000.0

    def __str__(self):
        return "<native fn>"


class Function(Stmt):
    name: Token
    body: List[Expr] = []
    params: List[Token] = []


@dataclass
class DubFunction(ICallable):
    declaration: Function
    closure: Optional[Environment] = None

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: "Interpreter", *args):
        environ = Environment(enclosing=self.closure)
        for arg, param in zip(args, self.declaration.params):
            environ.define(param.lexeme, arg)

        try:
            interpreter.execute_block(self.declaration.body, environ)
        except ReturnErr as ret:
            return ret.value

    def __str__(self):
        return f"<native {self.declaration.name.lexeme}>"


end_all(globals())