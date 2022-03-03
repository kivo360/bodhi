from functools import cached_property
from typing import Mapping

from auto_all import end_all
from auto_all import start_all
from sqlalchemy import Column

from .imports import CreateTable
from .imports import PostGDialect

start_all(globals())

psql_di = PostGDialect

from .clock import Clock
from .episodes import Episode
from .mappings import Mappings
from .raw import Unstructured
from .sessions import Sessions

timing = Clock
unstructured = Unstructured


class TableAdapter:
    @cached_property
    def data(self):
        """Returns the data column. Use to return the unstructured data column."""
        return unstructured.c.data

    @cached_property
    def tags(self) -> Column:
        """Returns the data column. Use to return the unstructured data column."""
        return unstructured.c.tags

    @cached_property
    def bucket(self) -> Column:
        """Returns the data column. Use to return the unstructured data column."""
        return unstructured.c.bucket

    @cached_property
    def reference_time(self) -> Column:
        """Returns the data column. Use to return the unstructured data column."""
        return unstructured.c.reference_time

    @cached_property
    def insert_time(self) -> Column:
        """Returns the data column. Use to return the unstructured data column."""
        return unstructured.c.insert_time


def crt_tbl(table) -> str:
    return CreateTable(table).compile(dialect = PostGDialect())


TBList = [Clock, Episode, Sessions, Unstructured, Mappings]

end_all(globals())
