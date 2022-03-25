import re
import warnings
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Mapping, Set, Type, Union
from uuid import UUID
from uuid import uuid4

from loguru import logger

from pampy import _
from pampy import match
from pydantic.fields import ModelField
from pydantic.json import pydantic_encoder
from pydantic.main import BaseModel  # noqa: F401
from pydantic.schema import get_flat_models_from_model
from pydantic.schema import get_model_name_map
from pydantic.schema import model_process_schema
from pydantic.types import Json
from pydantic.types import UUID4
from pydantic.utils import get_model
from pydantic.utils import lenient_issubclass
from pydantic.utils import ROOT_KEY
from pydantic.utils import sequence_like
from sqlalchemy import Boolean
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import dialect as PostGDialect
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import TSTZRANGE
from sqlalchemy.dialects.postgresql import UUID as PgUUID

from bodhi_server.generator.types import TimeSeriesRange
from bodhi_server.generator.types import Timestampz

TypeModelOrEnum = Union[Type["BaseModel"], Type[Enum]]
TypeModelSet = Set[TypeModelOrEnum]


class ObjectSqlMapper:
    __predicates = []

    def add(self, predicate, response: Any):
        self.__predicates += [predicate, lambda x: response]

    def get(self, field):
        self.__predicates += [_, lambda x: None]
        return match(field, *self.__predicates)


class ObjectSqlMapper(ObjectSqlMapper):
    def __init__(self) -> None:

        self.add(Union[datetime, date, timedelta, time], Timestampz)
        self.add(Union[str, bytes], Text)
        self.add(bool, Boolean)
        self.add(Union[dict, Dict, Mapping, Json], JSONB)
        self.add(int, Integer)
        self.add(Union[float, Decimal], Numeric)
        self.add(Union[UUID, UUID4], PgUUID(as_uuid=True))
        self.add(Union[TimeSeriesRange], TSTZRANGE)


def model_queries(
    model: Union[Type["BaseModel"]],
) -> Dict[str, Any]:
    """
    Generate a JSON Schema for one model. With all the sub-models defined in the ``definitions`` top-level
    JSON key.

    :param model: a Pydantic model (a class that inherits from BaseModel)
    :param by_alias: generate the schemas using the aliases defined, if any
    :param ref_prefix: the JSON Pointer prefix for schema references with ``$ref``, if None, will be set to the
      default of ``#/definitions/``. Update it if you want the schemas to reference the definitions somewhere
      else, e.g. for OpenAPI use ``#/components/schemas/``. The resulting generated schemas will still be at the
      top-level key ``definitions``, so you can extract them from there. But all the references will have the set
      prefix.
    :param ref_template: Use a ``string.format()`` template for ``$ref`` instead of a prefix. This can be useful for
      references that cannot be represented by ``ref_prefix`` such as a definition stored in another file. For a
      sibling json file in a ``/schemas`` directory use ``"/schemas/${model}.json#"``.
    :return: dict with the JSON Schema for the passed ``model``
    """
    model = get_model(model)
    flat_models = get_flat_models_from_model(model)
    model_name_map = get_model_name_map(flat_models)
    model_name = model_name_map[model]
    logger.debug(model_name)
    logger.info(model)
    logger.warning(model_name_map)
    # model_process_schema
    # m_schema, m_definitions, nested_models = model_process_schema(
    #     model, by_alias=by_alias, model_name_map=model_name_map, ref_prefix=ref_prefix, ref_template=ref_template
    # )
    # if model_name in nested_models:
    #     # model_name is in Nested models, it has circular references
    #     m_definitions[model_name] = m_schema
    #     m_schema = get_schema_ref(model_name, ref_prefix, ref_template, False)
    # if m_definitions:
    #     m_schema.update({'definitions': m_definitions})
    return {}


if __name__ == "__main__":
    pql_map = PostgresqlMapper()
    # print(pql_map.get(3))
