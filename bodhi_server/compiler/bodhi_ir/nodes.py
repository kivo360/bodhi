from typing import Any, Type, Union, Optional, Dict

from bodhi_server.compiler import OpType, BinopType, UnaryType, NodeType, TokenType
from bodhi_server.compiler.bodhi_ir.abc import IRNode, IRNodeConvert
from bodhi_server import utils

AstType = Union[TokenType, UnaryType, BinopType, NodeType, OpType, None]


class BinaryConvert(IRNodeConvert):
    def convert(self, node: "IRNode") -> Dict[str, Any]:
        resp = super().convert(node)
        resp["left"] = {}
        resp["right"] = {}
        return resp


class BodyConvert(IRNodeConvert):
    def convert(self, node: "IRNode") -> Dict[str, Any]:
        resp = super().convert(node)
        resp["body"] = []
        if hasattr(node, "identity"):
            resp["identifier"] = getattr(node, "identity")
        return resp


class ValueConvert(IRNodeConvert):
    def convert(self, node: "IRNode") -> Dict[str, Any]:
        resp = super().convert(node)
        resp["value"] = node.value
        return resp


# class BodyIdConvert(IRNodeConvert):
#     def convert(self, node: "IRNode") -> Dict[str, Any]:
#         resp = super().convert(node)

#         resp["name"] = getattr(node, "identity")
#         resp["body"] = []
#         return resp


class IrRead(IRNode):
    convert: BinaryConvert = BinaryConvert()

    @property
    def read_name(self) -> str:
        return utils.consistent_naming(self.__class__.__name__)


class IRBody(IRNode):
    convert: BodyConvert = BodyConvert()

    @property
    def read_name(self) -> str:
        return utils.consistent_naming(self.__class__.__name__)


class IRValue(IRNode):
    convert: ValueConvert = ValueConvert()

    @property
    def read_name(self) -> str:
        return utils.consistent_naming(self.__class__.__name__)


class Explicit(IRNode):
    value: Optional[Any] = None


class Group(IRNode):
    """Suggest that the function is written in a parenthesis."""


class BinOp(IrRead):
    """Binary operator."""


class UnaryOp(IrRead):
    pass


class Add(BinOp):
    type: AstType = BinopType.ADD
    name: str = "+"


class Subtract(BinOp):
    type: AstType = BinopType.SUB
    name: str = "-"


class Multiply(BinOp):
    type: AstType = BinopType.MUL
    name: str = "*"


class Divide(BinOp):
    type: AstType = BinopType.DIV
    name: str = "/"


class FloorDivide(BinOp):
    type: AstType = BinopType.FLOORDIV
    name: str = "//"


class Modulo(BinOp):
    type: AstType = BinopType.MOD
    name: str = "%"


class BitOr(BinOp):
    type: AstType = BinopType.BIT_OR
    name: str = "|"


class BitAnd(BinOp):
    type: AstType = BinopType.BIT_AND
    name: str = "&"


class BitXor(BinOp):
    type: AstType = BinopType.BIT_XOR
    name: str = "^"


class Greater(BinOp):
    type: AstType = BinopType.GT
    name: str = ">"


class GreaterEq(BinOp):
    type: AstType = BinopType.GE
    name: str = ">="


class Less(BinOp):
    type: AstType = BinopType.LT
    name: str = "<"


class LessEq(BinOp):
    type: AstType = BinopType.LE
    name: str = "<="


class Equals(BinOp):
    type: AstType = BinopType.EQ
    name: str = "=="


class NotEquals(BinOp):
    type: AstType = BinopType.NE
    name: str = "!="


class And(BinOp):
    type: AstType = OpType.AND
    name: str = "and"


class Or(BinOp):
    type: AstType = OpType.OR
    name: str = "or"


def get_binary(lexme: str) -> Type[IRNode]:
    return {
        "+": Add,
        "-": Subtract,
        "*": Multiply,
        "/": Divide,
        "//": FloorDivide,
        "%": Modulo,
        "|": BitOr,
        "&": BitAnd,
        "^": BitXor,
        ">": Greater,
        ">=": GreaterEq,
        "<": Less,
        "<=": LessEq,
        "==": Equals,
        "!=": NotEquals,
        "and": And,
        "or": Or,
    }[lexme]


class Plus(UnaryOp):
    type: AstType = BinopType.ADD
    name: str = "+"


class Minus(UnaryOp):
    type: AstType = BinopType.SUB
    name: str = "-"


class IsNot(UnaryOp):
    type: AstType = UnaryType.NOT
    name: str = "!"


class IsNotTxt(IRNode):
    type: AstType = UnaryType.NOT
    name: str = "not"


def get_unary(lexme: str) -> Type[IRNode]:
    # {"+": "Plus", "-": "Minus", "!": "IsNot", "not": "IsNotTxt"}
    return {
        "+": Plus,
        "-": Minus,
        "!": IsNot,
        "not": IsNotTxt,
    }[lexme]


class Program(IRBody):
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


class Function(IRBody):
    type: AstType = NodeType.FUNCTION
    name: str = "function"
    identity: str = ""
    # convert: BodyIdConvert = BodyIdConvert()


class Param(IRNode):
    type: AstType = NodeType.PARAM
    name: str = "param"
    identity: str = ""


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


class Value(IRValue):
    type: AstType = NodeType.VALUE
    name: str = "literal"


class Float(Value):
    name = "float"


class Int(Value):
    name = "int"


class String(Value):
    name = "string"


class Bool(Value):
    name = "boolean"


class Array(Value):
    name = "array"


class Module(IRBody):
    type: AstType = NodeType.MODULE
    name: str = "module"


def match_type(type_cmp: type):
    if type_cmp is float:
        return ""


def get_literal(val_type: type) -> Type[IRNode]:
    return {
        float: Float,
        int: Int,
        str: String,
        bool: Bool,
    }[val_type]
