# from pydantic.dataclasses import dataclass
import uuid
from functools import cached_property
from typing import Optional

from loguru import logger

from arango.graph import Graph
from pydantic import BaseModel

from bodhi_server import connection
from bodhi_server.graph_database.graph import CursorAccountant
from bodhi_server.graph_database.graph import Edge
from bodhi_server.graph_database.graph import EdgeQuery
from bodhi_server.graph_database.graph import Node
from bodhi_server.graph_database.utilz import gen_hex_id
from bodhi_server.graph_database.utilz import to_snake
from bodhi_server.settings import ModuleSettings


modset = ModuleSettings()


class GraphController(BaseModel):
    name: str
    locs: dict = {}

    def __init__(self, name: Optional[str] = None, **data):
        data["name"] = name or modset.arangoo.graph_name
        data["name"] = to_snake(data["name"])
        super().__init__(**data)

    @property
    def db(self):
        return connection.graph

    @property
    def graph(self) -> Graph:
        if "graph" in self.locs:
            return self.locs["graph"]

        if self.db.has_graph(self.name):
            self.locs["graph"] = self.db.graph(self.name)
        else:
            self.locs["graph"] = self.db.create_graph(self.name)

        return self.locs["graph"]

    def __get_collection(self, name: str):
        if self.graph.has_vertex_collection(name):
            return self.graph.vertex_collection(name)
        else:
            return self.graph.create_vertex_collection(name)

    def __get_edge_collection(self, _edge: Edge, is_replace: bool = False):
        if not self.graph.has_edge_definition(_edge.edge_type):
            return self.graph.create_edge_definition(**_edge.to_edge_def())
        if not is_replace:
            return self.graph.edge_collection(_edge.edge_type)
        return self.graph.replace_edge_definition(**_edge.to_edge_def())

    @logger.catch(reraise=True)
    def collection(
        self, name: str = "", edge: Optional[Edge] = None, is_replace: bool = False
    ):
        if edge is not None:
            return self.__get_edge_collection(edge, is_replace=is_replace)
        return self.__get_collection(name)

    def add_node(self, node: Node):
        self.collection(node.kind).insert(node.to_dict())

    def find_one_node(self, kind: str, tags: dict):
        # logger.warning((kind, tags))
        cursor = self.collection(kind).find(tags, limit=1)
        return CursorAccountant(self.collection(kind).find(tags, limit=1))
        # return cursor.next()

    def update_match(self, kind: str, tags: dict, vals: dict):
        col = self.collection(kind)
        col.update_match(tags, vals)
        return CursorAccountant(col.find(tags, limit=1))

    def get_adjacent(self, edge_query: EdgeQuery):
        # Get the edges for a given node. We wrap the query information into an edge class.
        query_node: Node = edge_query.start
        element_container = self.find_one_node(query_node.kind, query_node.record)
        logger.error(element_container)
        element = element_container.element

        # We pass the element id into a string query.
        verticies: dict = self.graph.traverse(
            start_vertex=element,
            direction="any",
            vertex_uniqueness="global",
            edge_uniqueness="global",
            max_depth=2,
        )
        verticies_only = verticies.get("vertices")
        if len(verticies_only) > 1:
            adjacent_node = verticies_only[-1]
            return adjacent_node
        return element_container

    def add_edge(self, edge_info: Edge):
        edge_col = self.collection(edge=edge_info)
        find_start = self.find_one_node(*edge_info.find_from())
        find_end = self.find_one_node(*edge_info.find_to())
        edge_col.insert(
            {
                "_key": gen_hex_id(),
                "_from": find_start.doc_id,
                "_to": find_end.doc_id,
                **edge_info.props,
            }
        )
        return edge_col
