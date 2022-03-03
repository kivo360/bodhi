# maestro
from dataclasses import dataclass
from typing import Optional

from loguru import logger

from pydantic import BaseModel

from mangostar.graph_database.graph import Namespace
from mangostar.graph_database.graph import Node


class NamespaceResponse(BaseModel):
    is_prior: bool = False
    prior_id: Optional[str] = None
    schema_hash: Optional[str] = None
    values: Optional[dict] = {}
    # data: Optional[dict] = {}
    # This is the response node.
    node: Optional[Node] = None
    node_acc: Optional[Namespace] = None

    class Config:
        extra = "ignore"

    def match_hash(self, json_schema_hash: str) -> bool:
        if self.schema_hash is None:
            return False
        logger.info(json_schema_hash)
        logger.warning(self.schema_hash)
        logger.info("")
        return self.schema_hash == json_schema_hash

    @property
    def is_schema(self) -> bool:
        return bool(self.schema_hash)


class SchemaResp(BaseModel):
    # This is the response node.
    node: Optional[Node] = None
