from bodhi_server.compiler import Token, TokenType
from .core import Logical
from auto_all import start_all, end_all

start_all(globals())


class And(Logical):
    token: Token = Token(token_type=TokenType.GREATER, lexeme="and")


class Or(Logical):
    token: Token = Token(token_type=TokenType.GREATER_EQUAL, lexeme="or")


end_all(globals())
