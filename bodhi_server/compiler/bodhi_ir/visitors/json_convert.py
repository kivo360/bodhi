from devtools import debug
from typing import Any, Dict, List, Type

from loguru import logger

import retworkx as rx
from rich import print
from toolz import itemfilter
from toolz import valfilter

from bodhi_server.compiler.bodhi_ir import Module
from bodhi_server.compiler.bodhi_ir import StmtOf
from bodhi_server.compiler.bodhi_ir import edges as ex
from bodhi_server.compiler.bodhi_ir.abc import AccessNode
from bodhi_server.compiler.bodhi_ir.abc import IREdge
from bodhi_server.compiler.bodhi_ir.abc import IRVisitor
from bodhi_server.compiler.bodhi_ir.abc import IValidator
from contextlib import contextmanager


def edge_filter(node_map: Dict[int, IREdge], check_type: Type) -> Dict[int, IREdge]:
    return valfilter(lambda x: isinstance(x, check_type), node_map)


@contextmanager
def stack_ctx(visitor: IRVisitor, *args, **kwds):
    """Usef before running through the stack"""
    # Code to acquire resource, e.g.:

    index = visitor.index

    try:
        yield
    finally:
        # Code to release resource, e.g.:
        visitor.index = index


class Validator(IValidator):
    def is_binary(self) -> bool:
        return super().is_binary()

    def is_body(self):
        childs = self.node.children_edge((StmtOf, ex.Body))
        # lucky = edge_filter(childs, StmtOf)
        return bool(childs)


class JsonVisitor(IRVisitor):
    def __init__(self, graph: rx.PyDiGraph) -> None:
        super().__init__(graph)
        self.validator = Validator

    def visit_binop(self, binop):
        binop_resp = {"type": binop.read_name}
        if binop.value is not None:
            binop_resp["value"] = binop.value
        self.json_resp[binop.name] = binop_resp

    def visit_unary(self, unary):
        unary_resp = {"type": unary.read_name}
        if unary.value is not None:
            unary_resp["value"] = unary.value
        self.json_resp[unary.name] = unary_resp

    def visit_module(self, node: AccessNode):
        # ctx_id = self.index
        node_dict = {"type": "module", "body": []}

        if not node.validator.is_body():
            # logger.info("There anything in the modules' body")
            raise ValueError("There is nothing in the modules' body")

        # body: List[Dict[str, Any]] = []
        with stack_ctx(self):
            for key, val in node.children_edge(StmtOf).items():
                # self.index = key
                node_dict["body"].append(self.visit(self.get_node(key, True)))  # type: ignore
            # node_dict["body"] = body

        # self.index = ctx_id
        return node_dict

    def visit_function(self, node: AccessNode):
        node_dict = {
            "type": "function",
            "body": [],
            "name": getattr(node.current, "identity"),
        }
        if not node.validator.is_body():
            raise ValueError("There is nothing in the functions' body")

        things = node.children_edge(StmtOf)
        logger.success(things)
        return node_dict

    def visit_edge_type(self, edge_type):
        edge_type_resp = {"type": edge_type.read_name}
        if edge_type.value is not None:
            edge_type_resp["value"]
