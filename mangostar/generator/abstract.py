"""
# Abstraction

This is the general abstraction to be able to create a bunch of queries. Will run this inside of the build process to generate sql queries automatically.
"""
import abc
import datetime
import uuid
from typing import Dict, Optional

import stringcase
from pydantic import UUID4, BaseModel, Field, Json, PrivateAttr, validator
from pydantic.fields import ModelField
from pydantic.utils import (
    ROOT_KEY, get_model, lenient_issubclass, sequence_like
)
from mangostar import sql_build as sqb
from sqlalchemy import MetaData, Table
from sqlalchemy.dialects import postgresql as psql

metadata = MetaData()


class ConvertableBaseModel(BaseModel, abc.ABC):
    id: UUID4 = uuid.uuid4()
    name: Optional[str]
    _table: Optional[Table] = None

    @validator('name', pre = True, always = True)
    def set_table_name(cls, v):
        return stringcase.snakecase(cls.__class__)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **columns) -> None:
        super().__init__(**columns)
        self._create_table()

    def _create_table(self):
        # Creates a table from all of the fields that aren't name.
        self.__fields__

    @classmethod
    def to_sql(cls):
        sqb.model_queries(cls)

    @property
    def table(self) -> Table:
        """
        Return the created table

        Returns
        -------
        Table
            The table of generated from the model.

        Raises
        ------
        AttributeError
            If the table hasn't been generated yet.
        """
        if self._table is None:
            raise AttributeError("Table doesn't exist")
        return self._table

    @property
    def table_name(self) -> str:
        return self.name


class RawData(ConvertableBaseModel):

    bucket: str = "random_bucket_name "
    data: Dict = {}
    tags: Dict = {}
    reference_time: datetime.datetime = datetime.datetime.now()
    insert_time: datetime.datetime = datetime.datetime.now()


print(RawData.to_sql())

rd_tab = RawData()
