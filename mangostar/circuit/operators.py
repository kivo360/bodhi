import abc
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from pydantic.dataclasses import dataclass
from mangostar.circuit.nodes import Node, Token
from mangostar.circuit.types import TokenType

CWD_DIR = Path.cwd()


class Expr(Node):
    pass


class Binary(Expr):
    left: Expr
    right: Expr
    token: Token


class Grouping(Expr):
    expression: Expr


class Literal(Expr):
    value: Any


class Unary(Expr):
    right: Expr
    token: Token


if __name__ == "__main__":
    # Try to turn something simple like this into a networkx graph.
    test_binary = Binary(
        right=Unary(
            token=Token(token_type=TokenType.MINUS, lexeme="-", literal=None, line=1),
            right=Literal(value=123),
        ),
        token=Token(token_type=TokenType.STAR, lexeme="*", literal=None, line=1),
        left=Grouping(expression=Literal(value=45.67)),
    )

    print(test_binary)
