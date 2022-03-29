from typing import Optional, Union

from loguru import logger

import orjson
from pydantic import BaseModel

from bodhi_server.settings import ModuleSettings

from .adapters.connection_adapter import ConnectionAdapter
from .core import (
    FlexibleModel,
    FlexibleModel as FlexModel,
    FlexibleModel as FModel,
    FlexibleModel as FMod,
    dataclass,
    base_conf,
    CommonConfig,
)

from .main import Component
from .main import Entity
from .main import Subsystem
from .main import system
from .main import System
from .main import Visitor
from .matches import Array
from .matches import ConstrNum
from .matches import get_field_type
from .matches import get_field_type as get_schema
from .matches import get_sql_nodes as match_sql
from .matches import is_array
from .matches import is_nested
from .matches import is_scalar
from .matches import is_top
from .matches import JsonSchemaParents
from .matches import JsonSchemaTypes
from .matches import Nested
from .matches import Scalar
from .matches import Top
from .relational import Field
from .relational import SQLVisitor
from .relational import Table
from .visitors import visit_json
import retworkx as rx


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


# logger.disable("bodhi_server")
# logger.disable("tests.integrations")
module_settings = ModuleSettings()
connection = ConnectionAdapter()
