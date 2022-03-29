from enum import Enum
from auto_all import start_all, end_all

start_all(globals())


class TokenType(str, Enum):
    # Single-character tokens.
    LEFT_PAREN = ("LEFT_PAREN",)
    RIGHT_PAREN = ("RIGHT_PAREN",)
    LEFT_BRACE = ("LEFT_BRACE",)
    RIGHT_BRACE = ("RIGHT_BRACE",)
    COMMA = ("COMMA",)
    DOT = ("DOT",)
    MINUS = ("MINUS",)
    PLUS = ("PLUS",)
    SEMICOLON = ("SEMICOLON",)
    SLASH = ("SLASH",)
    STAR = ("STAR",)
    DOUBLESTAR = ("DOUBLESTAR",)
    DOUBLESLASH = ("DOUBLESLASH",)

    # One or two character tokens.
    BANG = ("BANG",)
    BANG_EQUAL = ("BANG_EQUAL",)
    EQUAL = ("EQUAL",)
    NOT_EQUAL = ("NOT_EQUAL",)
    EQUAL_EQUAL = ("EQUAL_EQUAL",)
    GREATER = ("GREATER",)
    GREATER_EQUAL = ("GREATER_EQUAL",)
    LESS = ("LESS",)
    LESS_EQUAL = ("LESS_EQUAL",)
    IS_IN = ("IS_IN",)
    NOT_IN = ("NOT_IN",)
    IS = ("IS",)

    # Literals.
    IDENTIFIER = ("IDENTIFIER",)
    STRING = ("STRING",)
    NUMBER = ("NUMBER",)

    # Keywords.
    AND = ("AND",)
    CLASS = ("CLASS",)
    ELSE = ("ELSE",)
    IF = ("IF",)
    FALSE = ("FALSE",)
    FUN = ("FUN",)
    FOR = ("FOR",)
    NIL = ("NIL",)
    OR = ("OR",)
    PRINT = ("PRINT",)
    RETURN = ("RETURN",)
    SUPER = ("SUPER",)
    THIS = ("THIS",)
    TRUE = ("TRUE",)
    VAR = ("VAR",)
    WHILE = ("WHILE",)

    EOF = "EOF"


class EdgeTypes(str, Enum):
    ELSE = ("ELSE",)
    IF = ("IF",)
    BODY = ("BODY",)
    BRANCH_FALSE = ("BRANCH_FALSE",)
    BRANCH_TRUE = ("BRANCH_TRUE",)
    CONDITION = ("CONDITION",)
    LEFT = ("EXPR_LEFT",)
    RIGHT = ("EXPR_RIGHT",)
    EXPR = ("EXPR",)
    VALUE = ("VALUE",)


class OpType(str, Enum):
    NONE = ("NONE",)
    ASSIGNMENT = ("ASSIGNMENT",)
    OR = ("OR",)
    AND = ("AND",)
    EQUALITY = ("EQUALITY",)
    COMPARISON = ("COMPARISON",)
    TERM = ("TERM",)
    FACTOR = ("FACTOR",)
    UNARY = ("UNARY",)
    CALL = ("CALL",)
    PRIMARY = ("PRIMARY",)


class UnaryType(str, Enum):
    NOT = ("NOT",)
    MINUS = ("MINUS",)
    PLUS = ("PLUS",)


class BinopType(str, Enum):
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    FLOORDIV = "FLOORDIV"
    MOD = "MOD"
    BIT_OR = "BIT_OR"
    BIT_AND = "BIT_AND"
    BIT_XOR = "BIT_XOR"
    BIT_LSHIFT = "BIT_LSHIFT"
    BIT_RSHIFT = "BIT_RSHIFT"
    LT = "LT"
    LE = "LE"
    GT = "GT"
    GE = "GE"
    EQ = "EQ"
    NE = "NE"
    IN = "IN"
    NOT_IN = "NOT_IN"
    IS = "IS"
    IS_NOT = "IS_NOT"
    AND = "AND"
    OR = "OR"


class NodeType(str, Enum):
    PROGRAM = "PROGRAM"
    EXPRSTMT = "EXPRSTMT"
    VARIABLE = "VARIABLE"
    ASSIGN = "ASSIGN"
    BLOCK = "BLOCK"
    IF = "IF"
    WHILE = "WHILE"
    CALL = "CALL"
    RETURN = "RETURN"
    LOGICAL = "LOGICAL"
    FUNCTION = "FUNCTION"
    CLASS = "CLASS"
    EXPR = "EXPR"
    FOR = "FOR"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    VALUE = "VALUE"


class Flavor(Enum):
    """Flavor describes the kind of object a node represents."""

    UNSPECIFIED = "---"  # as it says on the tin
    UNKNOWN = "???"  # not determined by analysis (wildcard)

    NAMESPACE = "namespace"  # node representing a namespace
    ATTRIBUTE = "attribute"  # attr of something, but not known if class or func.

    IMPORTEDITEM = "import"  # imported item of unanalyzed type

    MODULE = "module"
    GLOBAL = "global"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"  # instance method
    STATICMETHOD = "staticmethod"
    CLASSMETHOD = "classmethod"
    NAME = "name"  # Python name (e.g. "x" in "x = 42")
    BLOCK = "block"  # Python name (e.g. "x" in "x = 42")

    @staticmethod
    def specificity(flavor):

        if flavor in (Flavor.UNSPECIFIED, Flavor.UNKNOWN):
            return 0
        elif flavor in (Flavor.NAMESPACE, Flavor.ATTRIBUTE):
            return 1
        elif flavor == Flavor.IMPORTEDITEM:
            return 2
        else:
            return 3


end_all(globals())
