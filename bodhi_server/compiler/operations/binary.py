from bodhi_server.compiler import Binary
from bodhi_server.compiler import Token
from bodhi_server.compiler import BinopType
from bodhi_server.compiler import NodeType, Expr

from auto_all import start_all, end_all

start_all(globals())


class Add(Binary):
    token: Token = Token(token_type=BinopType.ADD, lexeme="+")


class Subtract(Binary):
    token: Token = Token(token_type=BinopType.SUB, lexeme="-")


class Multiply(Binary):
    token: Token = Token(token_type=BinopType.MUL, lexeme="*")


class Divide(Binary):

    token: Token = Token(token_type=BinopType.DIV, lexeme="/")


def div(left: Expr, right: Expr) -> Divide:
    return Divide(left=left, right=right)


def add(left: Expr, right: Expr) -> Add:
    return Add(left=left, right=right)


def sub(left: Expr, right: Expr) -> Subtract:
    return Subtract(left=left, right=right)


def mul(left: Expr, right: Expr) -> Multiply:
    return Multiply(left=left, right=right)


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
