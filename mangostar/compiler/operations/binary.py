from .core import Binary
from mangostar.compiler import Token
from mangostar.compiler import TokenType
from auto_all import start_all, end_all

start_all(globals())


class Add(Binary):
    token: Token = Token(token_type=TokenType.PLUS, lexeme="+")


class Subtract(Binary):
    token: Token = Token(token_type=TokenType.MINUS, lexeme="-")


class Multiply(Binary):
    token: Token = Token(token_type=TokenType.STAR, lexeme="*")


class Divide(Binary):

    token: Token = Token(token_type=TokenType.SLASH, lexeme="/")


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
