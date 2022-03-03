import os
import uuid

from devtools import debug

from arango.graph import Graph
from faker import Faker

from mangostar.graph_database._controller import GraphController
from mangostar.graph_database.graph import Edge
from mangostar.graph_database.graph import EdgeQuery
from mangostar.graph_database.graph import Node
from mangostar.utils import *


GRAPH_NAME = "testing_graph"
NODE_KIND = "test_kind"
NODE_BASE_NAME = "test_node"
NODE_EXPLAINER = {"searchably": "rekted", "is": "king"}


def idgen() -> str:
    _id = uuid.uuid4().hex
    return f"{NODE_BASE_NAME}_{_id}"


def append_id(string_value: str) -> str:
    _id = uuid.uuid4().hex
    return f"{string_value}_{_id}"


os.environ["ARANOGO_DATABASE"] = f"{GRAPH_NAME}_{idgen()}"

fake = Faker()


def test_create_graph():
    graph_controller = GraphController(append_id(GRAPH_NAME))
    graph_obj: Graph = graph_controller.graph
    assert graph_obj
    assert isinstance(graph_obj, Graph)


def test_create_node():
    graph_controller = GraphController(append_id(GRAPH_NAME))
    graph_obj: Graph = graph_controller.graph
    assert graph_obj
    assert isinstance(graph_obj, Graph)
    node = Node(NODE_KIND, idgen(), NODE_EXPLAINER)

    # Attempting to add a single node
    graph_controller.add_node(node)


def test_create_edge():
    graph_controller = GraphController(append_id(GRAPH_NAME))

    node_one = Node(NODE_KIND, idgen(), NODE_EXPLAINER)
    node_two = Node(NODE_KIND, idgen(), NODE_EXPLAINER)

    graph_controller.add_node(node_one)
    graph_controller.add_node(node_two)

    edge_one = Edge(
        edge_type="test_edge_type",
        start=node_one,
        end=node_two,
        props={"hello": "world"},
    )

    graph_controller.add_edge(edge_one)
    assert True


def test_get_adjacent_nodes():
    graph_controller = GraphController(append_id(GRAPH_NAME))
    edge_kind = append_id("noob_kind")
    node_kind = append_id(NODE_BASE_NAME)
    node_one = Node(node_kind, idgen(), NODE_EXPLAINER)
    node_two = Node(node_kind, idgen(), NODE_EXPLAINER)

    graph_controller.add_node(node_one)
    graph_controller.add_node(node_two)
    edge_one = Edge(
        edge_type=edge_kind,
        start=node_one,
        end=node_two,
        props={"hello": "world"},
    )

    graph_controller.add_edge(edge_one)
    adjacent = graph_controller.get_adjacent(
        EdgeQuery(
            edge_type=edge_kind,
            start=node_one,
            props={"hello": "world"},
        )
    )
    debug(adjacent)
    assert not adjacent.is_empty, "There should be at least one node available."
