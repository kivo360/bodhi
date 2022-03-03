import abc
import uuid
from dataclasses import dataclass
from typing import Optional

from arango import cursor
from auto_all import end_all
from auto_all import start_all
from cytoolz import curry
from pydantic import BaseModel
from pydantic import Field
from stringcase import snakecase

from mangostar.graph_database._enums import Direction


start_all(globals())


@dataclass
class Node:
    kind: str
    name: str
    record: dict

    def to_dict(self):
        return {"_key": self.name, **self.record}

    def to_find(self):
        return self.kind, self.record


@dataclass(frozen=True)
class ViewParams:
    username: str
    stakeholder: str
    project: str


# username
# stakeholder
# project


class Edge(BaseModel):
    edge_type: str = Field(..., description="The type of edge we're adding in.")
    start: Node
    end: Node
    props: dict = Field(..., description="A bunch of properties for a graph.")

    def to_edge_def(self):
        return dict(
            edge_collection=self.edge_type,
            from_vertex_collections=[self.start.kind],
            to_vertex_collections=[self.end.kind],
        )

    def find_from(self):
        return self.start.to_find()

    def find_to(self):
        return self.end.to_find()


class EdgeQuery(BaseModel):
    edge_type: str
    start: Node
    props: dict = {}
    direction: Direction = Direction.OUT


class CursorAccountant:
    curse: cursor.Cursor

    def __init__(self, cursor: cursor.Cursor):
        self.init_placeholder = None
        self._count = cursor._count
        if not self.is_empty:
            self.init_placeholder = cursor.next()
        self.curse = cursor

    # class Config:
    #     arbitrary_types_allowed = True

    @property
    def is_empty(self):
        return self._count <= 0

    @property
    def element(self):
        if self.is_empty:
            raise AttributeError("Element doesn't exist")
        return self.init_placeholder

    @property
    def doc_id(self) -> str:
        return self.init_placeholder["_id"]

    def yield_all(self):
        while cursor.has_more():  # Fetch until nothing is left on the server.
            yield cursor.fetch()


class NodeAccount(BaseModel, abc.ABC):
    class Config:
        arbitrary_types_allowed = True
        extras = "ignore"

    @property
    def space_name(self) -> str:
        return snakecase(self.__class__.__name__).lower()

    def to_node(self):
        return Node(self.space_name, uuid.uuid4().hex, self.dict(exclude_none=True))

    def to_find(self):
        return self.to_node().to_find()


class Namespace(NodeAccount):
    username: str
    stakeholder: str
    project: str


class SchemaSpot(NodeAccount):
    schema_def: dict
    project: str


class ViewNamespace(Namespace):
    view_name: str
    schema_hash: Optional[str] = None

    def __init__(
        self,
        *,
        username: str,
        stakeholder: str,
        project: str,
        view_name: str,
        schema_hash: Optional[str] = None,
        **data
    ):
        data["username"] = username
        data["stakeholder"] = stakeholder
        data["project"] = project
        data["view_name"] = view_name
        data["schema_hash"] = schema_hash
        super().__init__(**data)

    @property
    def space_name(self) -> str:
        return snakecase("namespace").lower()


def create_query(
    edge_type: str, start: Node, props: dict = {}, direction: Direction = Direction.OUT
) -> EdgeQuery:
    """Creates an edge query injection.

    Args:
        edge_type (str): [description]
        start (Node): [description]
        props (dict, optional): [description]. Defaults to {}.
        direction (Direction, optional): [description]. Defaults to Direction.OUT.

    Returns:
        EdgeQuery: [description]
    """
    return EdgeQuery(edge_type=edge_type, start=start, props=props, direction=direction)


@curry
def create_edge(edge_type: str, start: Node, end: Node, props: dict = {}):
    return Edge(edge_type=edge_type, start=start, end=end, props=props)


end_all(globals())
