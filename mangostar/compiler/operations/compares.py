from .core import Logical
from mangostar.compiler import Token, TokenType

from auto_all import start_all, end_all

start_all(globals())


class Greater(Logical):
    token: Token = Token(token_type=TokenType.GREATER, lexeme=">")


class GreaterEq(Logical):
    token: Token = Token(token_type=TokenType.GREATER_EQUAL, lexeme=">=")


class Less(Logical):
    token: Token = Token(token_type=TokenType.LESS, lexeme="<=")


class LessEq(Logical):
    token: Token = Token(token_type=TokenType.LESS_EQUAL, lexeme="<=")


class Equal(Logical):
    token: Token = Token(token_type=TokenType.LESS_EQUAL, lexeme="==")


class NotEqual(Logical):
    token: Token = Token(token_type=TokenType.NOT_EQUAL, lexeme="!=")


class Is(Logical):
    token: Token = Token(token_type=TokenType.IS, lexeme="is")


class IsIn(Logical):
    token: Token = Token(token_type=TokenType.IS_IN, lexeme="in")


class IsNot(Logical):
    token: Token = Token(token_type=TokenType.IS_IN, lexeme="is not")


class NotIn(Logical):
    token: Token = Token(token_type=TokenType.NOT_IN, lexeme="not in")


end_all(globals())

"""
TODO: Create all of the binary expressions as a placeholder for the python language.
class Add(Binary):
    token: Token = Token(token_type=TokenType.SLASH, lexeme="/")
class BitAnd(Binary):
    token: Token = Token(token_type=TokenType.SLASH, lexeme="/")
class BitOr(Binary):
    token: Token = Token(token_type=TokenType.SLASH, lexeme="/")
class BitXor(Binary):
    token: Token = Token(token_type=TokenType.SLASH, lexeme="/")
class Divide(Binary):
    token: Token = Token(token_type=TokenType.SLASH, lexeme="/")
class FloorDivide(Binary):
    token: Token = Token(token_type=TokenType.SLASH, lexeme="/")
class LeftShift(Binary):
    token: Token = Token(token_type=TokenType.SLASH, lexeme="/")
class MatrixMultiply(Binary):
    token: Token = Token(token_type=TokenType.SLASH, lexeme="/")
class Modulo(Binary):
    token: Token = Token(token_type=TokenType.SLASH, lexeme="/")
class Multiply(Binary):
    token: Token = Token(token_type=TokenType.SLASH, lexeme="/")
class Power(Binary):
    token: Token = Token(token_type=TokenType.SLASH, lexeme="/")
class RightShift(Binary):
    token: Token = Token(token_type=TokenType.SLASH, lexeme="/")

"""
