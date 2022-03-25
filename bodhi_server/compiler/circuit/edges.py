from typing import Any, Optional
from bodhi_server import FlexModel
from abc import ABC
from bodhi_server.compiler import Token, TokenType, EdgeTypes
from bodhi_server.compiler.circuit.core import ASTEdge


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
