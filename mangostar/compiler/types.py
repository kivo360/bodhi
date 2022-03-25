from enum import Enum


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
    FALSE = ("FALSE",)
    FUN = ("FUN",)
    FOR = ("FOR",)
    IF = ("IF",)
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