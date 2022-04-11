from typing import Any, Union, Optional

from bodhi_server.compiler import OpType, BinopType, UnaryType, NodeType, TokenType
from bodhi_server.compiler.bodhi_ir.abc import IRNode

AstType = Union[TokenType, UnaryType, BinopType, NodeType, OpType, None]


class Explicit(IRNode):
    value: Optional[Any] = None


class Group(IRNode):
    """Suggest that the function is written in a parenthesis."""


class Binary(IRNode):
    """Binary operator."""


class Unary(IRNode):
    pass


class Add(IRNode):
    type: AstType = BinopType.ADD
    name: str = "+"


class Subtract(IRNode):
    type: AstType = BinopType.SUB
    name: str = "-"


class Multiply(IRNode):
    type: AstType = BinopType.MUL
    name: str = "*"


class Divide(IRNode):
    type: AstType = BinopType.DIV
    name: str = "/"


class FloorDivide(IRNode):
    type: AstType = BinopType.FLOORDIV
    name: str = "//"


class Modulo(IRNode):
    type: AstType = BinopType.MOD
    name: str = "%"


class BitOr(IRNode):
    type: AstType = BinopType.BIT_OR
    name: str = "|"


class BitAnd(IRNode):
    type: AstType = BinopType.BIT_AND
    name: str = "&"


class BitXor(IRNode):
    type: AstType = BinopType.BIT_XOR
    name: str = "^"


class Greater(IRNode):
    type: AstType = BinopType.GT
    name: str = ">"


class GreaterEq(IRNode):
    type: AstType = BinopType.GE
    name: str = ">="


class Less(IRNode):
    type: AstType = BinopType.LT
    name: str = "<"


class LessEq(IRNode):
    type: AstType = BinopType.LE
    name: str = "<="


class Equals(IRNode):
    type: AstType = BinopType.EQ
    name: str = "=="


class NotEquals(IRNode):
    type: AstType = BinopType.NE
    name: str = "!="


class And(IRNode):
    type: AstType = OpType.AND
    name: str = "and"


class Or(IRNode):
    type: AstType = OpType.OR
    name: str = "or"


class Plus(IRNode):
    type: AstType = BinopType.ADD
    name: str = "+"


class Minus(IRNode):
    type: AstType = BinopType.SUB
    name: str = "-"


class IsNot(IRNode):
    type: AstType = UnaryType.NOT
    name: str = "!"


class IsNotTxt(IRNode):
    type: AstType = UnaryType.NOT
    name: str = "not"


class Program(IRNode):
    type: AstType = NodeType.PROGRAM
    name: str = "program"


class Class(IRNode):
    type: AstType = NodeType.CLASS
    name: str = "class"


class ExprStmt(IRNode):
    type: AstType = NodeType.EXPRSTMT
    name: str = "exprstmt"


class Variable(IRNode):
    type: AstType = NodeType.VARIABLE
    name: str = "variable"


class Assign(IRNode):
    type: AstType = NodeType.ASSIGN
    name: str = "assign"


class Block(IRNode):
    type: AstType = NodeType.BLOCK
    name: str = "block"


class If(IRNode):
    type: AstType = NodeType.IF
    name: str = "if"


class While(IRNode):
    type: AstType = NodeType.WHILE
    name: str = "while"


class Call(IRNode):
    type: AstType = NodeType.CALL
    name: str = "call"


class Return(IRNode):
    type: AstType = NodeType.RETURN
    name: str = "return"


class Logical(IRNode):
    type: AstType = NodeType.LOGICAL
    name: str = "logical"


class Function(IRNode):
    type: AstType = NodeType.FUNCTION
    name: str = "function"


class Expr(IRNode):
    type: AstType = NodeType.EXPR
    name: str = "expr"


class For(IRNode):
    type: AstType = NodeType.FOR
    name: str = "for"


class Break(IRNode):
    type: AstType = NodeType.BREAK
    name: str = "break"


class Continue(IRNode):
    type: AstType = NodeType.CONTINUE
    name: str = "continue"
