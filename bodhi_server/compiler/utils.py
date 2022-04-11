from bodhi_server.compiler import Token, TokenType, Binary, Unary
from bodhi_server.compiler import Binary, Literal, Expr
from addict import Dict

# from bodhi_server.compiler import Binary
from auto_all import start_all, end_all


def new_token(tyoken_type: TokenType, lexeme: str):
    return Token(token_type=tyoken_type, lexeme=lexeme)


def is_binary(val) -> bool:
    return isinstance(val, Binary)


def is_lit(val) -> bool:
    return isinstance(val, Literal)


def is_unary(val) -> bool:
    return isinstance(val, Unary)


def flexify(val: dict):
    return Dict(val)
