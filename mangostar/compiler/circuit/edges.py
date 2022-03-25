from typing import Any, Optional
from mangostar import FlexModel
from abc import ABC
from mangostar.compiler import Token, TokenType, EdgeTypes
from mangostar.compiler.circuit.core import ASTEdge


class Expr(ASTEdge):
    type: EdgeTypes = EdgeTypes.EXPR


class Left(ASTEdge):
    type: EdgeTypes = EdgeTypes.LEFT


class Right(ASTEdge):
    type: EdgeTypes = EdgeTypes.RIGHT


class IsTrue(ASTEdge):
    type: EdgeTypes = EdgeTypes.BRANCH_TRUE


class IsFalse(ASTEdge):
    type: EdgeTypes = EdgeTypes.BRANCH_FALSE
