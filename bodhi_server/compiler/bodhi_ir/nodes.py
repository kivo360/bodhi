from typing import Any, Union, Optional

from bodhi_server.compiler import OpType, BinopType, UnaryType, NodeType, TokenType
from bodhi_server.compiler.bodhi_ir.abc import ASTNode

AstType = Union[TokenType, UnaryType, BinopType, NodeType, OpType, None]


class Explicit(ASTNode):
    value: Optional[Any] = None


class Group(ASTNode):
    """Suggest that the function is written in a parenthesis."""


class Binary(ASTNode):
    """Binary operator."""


class Unary(ASTNode):
    pass


class Add(ASTNode):
    type: AstType = BinopType.ADD
    name: str = "+"


class Subtract(ASTNode):
    type: AstType = BinopType.SUB
    name: str = "-"


class Multiply(ASTNode):
    type: AstType = BinopType.MUL
    name: str = "*"


class Divide(ASTNode):
    type: AstType = BinopType.DIV
    name: str = "/"


class FloorDivide(ASTNode):
    type: AstType = BinopType.FLOORDIV
    name: str = "//"


class Modulo(ASTNode):
    type: AstType = BinopType.MOD
    name: str = "%"


class BitOr(ASTNode):
    type: AstType = BinopType.BIT_OR
    name: str = "|"


class BitAnd(ASTNode):
    type: AstType = BinopType.BIT_AND
    name: str = "&"


class BitXor(ASTNode):
    type: AstType = BinopType.BIT_XOR
    name: str = "^"


class Greater(ASTNode):
    type: AstType = BinopType.GT
    name: str = ">"


class GreaterEq(ASTNode):
    type: AstType = BinopType.GE
    name: str = ">="


class Less(ASTNode):
    type: AstType = BinopType.LT
    name: str = "<"


class LessEq(ASTNode):
    type: AstType = BinopType.LE
    name: str = "<="


class Equals(ASTNode):
    type: AstType = BinopType.EQ
    name: str = "=="


class NotEquals(ASTNode):
    type: AstType = BinopType.NE
    name: str = "!="


class And(ASTNode):
    type: AstType = OpType.AND
    name: str = "and"


class Or(ASTNode):
    type: AstType = OpType.OR
    name: str = "or"


class Plus(ASTNode):
    type: AstType = BinopType.ADD
    name: str = "+"


class Minus(ASTNode):
    type: AstType = BinopType.SUB
    name: str = "-"


class IsNot(ASTNode):
    type: AstType = UnaryType.NOT
    name: str = "!"


class IsNotTxt(ASTNode):
    type: AstType = UnaryType.NOT
    name: str = "not"


class Program(ASTNode):
    type: AstType = NodeType.PROGRAM
    name: str = "program"


class Class(ASTNode):
    type: AstType = NodeType.CLASS
    name: str = "class"


class ExprStmt(ASTNode):
    type: AstType = NodeType.EXPRSTMT
    name: str = "exprstmt"


class Variable(ASTNode):
    type: AstType = NodeType.VARIABLE
    name: str = "variable"


class Assign(ASTNode):
    type: AstType = NodeType.ASSIGN
    name: str = "assign"


class Block(ASTNode):
    type: AstType = NodeType.BLOCK
    name: str = "block"


class If(ASTNode):
    type: AstType = NodeType.IF
    name: str = "if"


class While(ASTNode):
    type: AstType = NodeType.WHILE
    name: str = "while"


class Call(ASTNode):
    type: AstType = NodeType.CALL
    name: str = "call"


class Return(ASTNode):
    type: AstType = NodeType.RETURN
    name: str = "return"


class Logical(ASTNode):
    type: AstType = NodeType.LOGICAL
    name: str = "logical"


class Function(ASTNode):
    type: AstType = NodeType.FUNCTION
    name: str = "function"


class Expr(ASTNode):
    type: AstType = NodeType.EXPR
    name: str = "expr"


class For(ASTNode):
    type: AstType = NodeType.FOR
    name: str = "for"


class Break(ASTNode):
    type: AstType = NodeType.BREAK
    name: str = "break"


class Continue(ASTNode):
    type: AstType = NodeType.CONTINUE
    name: str = "continue"


class Value(ASTNode):
    type: AstType = NodeType.VALUE
    name: str = "literal"
