from typing import Any, Optional
from bodhi_server import FlexModel
from abc import ABC
from bodhi_server.compiler import Token, TokenType, EdgeTypes
from bodhi_server.compiler.bodhi_ir.abc import IREdge
from auto_all import start_all, end_all


start_all(globals())


class Expr(IREdge):
    type: EdgeTypes = EdgeTypes.EXPR


class Left(IREdge):
    type: EdgeTypes = EdgeTypes.LEFT


class Right(IREdge):
    type: EdgeTypes = EdgeTypes.RIGHT


class IsTrue(IREdge):
    type: EdgeTypes = EdgeTypes.BRANCH_TRUE


class IsFalse(IREdge):
    type: EdgeTypes = EdgeTypes.BRANCH_FALSE


class Condition(IREdge):
    type: EdgeTypes = EdgeTypes.BRANCH_FALSE


class GroupIn(Expr):
    pass


class Value(IREdge):
    type: EdgeTypes = EdgeTypes.VALUE


class Body(IREdge):
    type: EdgeTypes = EdgeTypes.VALUE


class StmtOf(IREdge):
    type: EdgeTypes = EdgeTypes.STMT_OF
    index: int = 0


class Param(IREdge):
    type: EdgeTypes = EdgeTypes.PARAMS
    local_id: int = 0


end_all(globals())
