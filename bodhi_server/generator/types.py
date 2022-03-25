from datetime import datetime

from sqlalchemy.sql import sqltypes
from sqlalchemy.dialects.postgresql import (UUID as PgUUID, TSTZRANGE)
from typing import Type, Any
from pydantic import BaseModel # noqa: F401
from typing import Dict


class Timestampz(sqltypes.TIMESTAMP):

    def __init__(self, precision=None):
        super(Timestampz, self).__init__(timezone=True)
        self.precision = precision


class TimeSeriesRange(BaseModel):
    begin: datetime = datetime.now()
    end: datetime = datetime.now()


class IndexedWrapper:
    pass


class IndexMeta(type):
    """
    Index Metadata

    Use this type to add an index to an indexable type and also do other things as well.

    Parameters
    ----------
    type : [type]
        [description]
    """

    def __getitem__(self, t: Type[sqltypes.Indexable]) -> Type[IndexedWrapper]:
        return type('IndexedValue', (IndexedWrapper,), {'inner_type': t})


class Index(metaclass=IndexMeta):

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type='string')
