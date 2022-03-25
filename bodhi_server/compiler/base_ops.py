import abc
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from pydantic import Field
from bodhi_server.compiler.abcs import Node, Token
from bodhi_server.compiler.types import TokenType


from auto_all import end_all, start_all


CWD_DIR = Path.cwd()

start_all(globals())


class Expr(Node):
    """An expression can be anything."""

    pass


class Stmt(Node):
    """A statement inside of the internal programming language"""

    pass


class Binary(Expr):
    left: Expr
    right: Expr
    token: Token


class Grouping(Expr):
    expr: Expr


class Literal(Expr):
    value: Any


class Unary(Expr):
    expr: Expr
    token: Token


end_all(globals())


#
# class Callable(Stmt):
#     callee: Expr
#     paren: Token
#     arguments: Expr


if __name__ == "__main__":
    # Try to turn something simple like this into a networkx graph.
    test_binary = Binary(
        right=Unary(
            expr=Literal(value=123),
            token=Token(token_type=TokenType.MINUS, lexeme="-", literal=None, line=1),
        ),
        token=Token(token_type=TokenType.STAR, lexeme="*", literal=None, line=1),
        left=Grouping(expr=Literal(value=45.67)),
    )

    print(test_binary)
