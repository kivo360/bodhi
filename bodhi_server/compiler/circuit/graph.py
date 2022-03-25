""" This is a compuational graph containing. It is a graph of nodes and edges that represents the AST of the underlying python code."""
from typing import Dict, Optional, Set
import retworkx as rx

from bodhi_server import FlexModel
from bodhi_server.compiler import (
    Token,
    TokenType,
    Stmt,
    Expr,
    Unary,
    Binary,
    Grouping,
    Literal,
    INodeDecomp,
    IASTGraph,
    EdgeTypes,
)
from PIL import Image
from bodhi_server.compiler.circuit.core import ASTEdge, ASTNode, ExprEdge, Left, Right
from bodhi_server.compiler.circuit import edges as ex
from bodhi_server.compiler.circuit import nodes as nxd
from bodhi_server import logger
from bodhi_server import utils


class Circuit(FlexModel, IASTGraph):
    name: str
    multi_graph: rx.PyDAG = rx.PyDAG()
    wires: Set[str] = set()
    input_map: Dict[str, str] = {}
    output_map: Dict[str, str] = {}
    op_nodes: Dict[str, str] = {}

    @property
    def graph(self):
        """The graph property."""
        return self.multi_graph

    @graph.setter
    def graph(self, value: rx.PyDAG):
        self.multi_graph = value


class UnaryDecomp(INodeDecomp):
    def decompose(self, node: Unary):
        logger.warning(node)
        node_obj = ASTNode(name=utils.hexid(), type=node.token.token_type)
        unary_idx = self.env.graph.add_node(node_obj)

        self.env.graph.add_child(unary_idx, node.expr.decompose(self.env), ex.Expr())
        # self.env.add_edge(node.expr, node, EdgeTypes.UNARY)
        logger.success(unary_idx)
        return unary_idx


class BinaryDecomp(INodeDecomp):
    def decompose(self, node: Binary, parent_id: int = -1):
        node_obj = ASTNode(name=utils.hexid(), type=node.token.token_type)
        binop_idx = self.env.graph.add_node(node_obj)
        right_node = node.right.decompose(self.env)
        left_node = node.left.decompose(self.env)

        self.env.graph.add_child(binop_idx, right_node, Right())
        self.env.graph.add_child(binop_idx, left_node, Left())
        utils.graphviz_show(
            self.env.graph, node_attr_fn=lambda node: {"label": str(node)}
        )
        return binop_idx


class GroupDecomp(INodeDecomp):
    def decompose(self, node: Binary, parent_id: int = -1):
        node_obj = ASTNode(name=utils.hexid(), type=node.token.token_type)
        binop_idx = self.env.graph.add_node(node_obj)
        right_node = node.right.decompose(self.env)
        left_node = node.left.decompose(self.env)

        self.env.graph.add_child(binop_idx, right_node, Right())
        self.env.graph.add_child(binop_idx, left_node, Left())
        utils.graphviz_show(
            self.env.graph, node_attr_fn=lambda node: {"label": str(node)}
        )
        return binop_idx

        # edge = ASTEdge(type=node.token.token_type)
        # logger.success(f"{right_idx} {left_idx}")

        # print(self.env.graph.nodes())
        # self.graph.add_node(node.right)
        # self.graph.add_edge(node.left, node.right, edge)


def main():

    from retworkx.visualization import graphviz_draw
    from matplotlib.pyplot import imshow
    from devtools import debug

    # Create a job dag
    # dependency_dag = rx.PyDiGraph(check_cycle=True)  # type: ignore
    # job_a = dependency_dag.add_node("Job A")
    # job_b = dependency_dag.add_child(job_a, "Job B", None)
    # job_c = dependency_dag.add_child(job_b, "Job C", None)
    # job_d = dependency_dag.add_child(job_a, "Job D", None)
    # job_e = dependency_dag.add_parent(job_d, "Job E", None)
    # job_f = dependency_dag.add_child(job_e, "Job F", None)
    # logger.info(job_f)
    # dependency_dag.add_edge(job_a, job_f, None)
    # dependency_dag.add_edge(job_c, job_d, None)

    # drawn.show()
    net = Circuit(name="ComputeGraph")

    binop = Binary(
        node_decomposer=BinaryDecomp(),
        right=Unary(
            node_decomposer=UnaryDecomp(),
            expr=Literal(value=123),
            token=Token(token_type=TokenType.MINUS, lexeme="-", literal=None, line=1),
        ),
        token=Token(token_type=TokenType.STAR, lexeme="*", literal=None, line=1),
        left=Grouping(expr=Literal(value=45.67)),
    )
    # debug(net)
    debug(binop.decompose(net))


if __name__ == "__main__":
    main()
