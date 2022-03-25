from typing import Union

from inflection import parameterize
from inflection import underscore

from humanize import precisedelta
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ColumnClause
from sqlalchemy.sql.expression import ColumnElement
from sqlalchemy.sql.expression import Selectable
from sqlalchemy.sql.functions import FunctionElement

# Might come back to this later. Ran into some serious problems whiile trying to index.


class create_hypertable(ColumnElement):
    def __init__(
        self,
        table_name: Union[Selectable, str],
        column_name: Union[ColumnElement, str]
    ):
        self.table_name: str = table_name.key if isinstance(
            table_name, Selectable
        ) else table_name
        self.column_name: str = column_name if isinstance(
            column_name, ColumnElement
        ) else column_name


@compiles(create_hypertable, 'postgresql')
def visit_hypertable(element: create_hypertable, compiler, **kw):
    tn = element.table_name
    cn = element.column_name
    return f"create_hypertable({tn}, {cn})"


class time_bucket(ColumnClause):
    def __init__(self, name: str, timestamp: Union[float, int]):
        self.name: str = name
        self.timestamp: int = timestamp


# TODO: Reorg to utils


def humanize_time(time_interval: str):
    if isinstance(time_interval, str):
        return time_interval
    elif isinstance(time_interval, (int, float)):
        return precisedelta(time_interval)
    raise ValueError("time_interval must be a string or number")


@compiles(time_bucket)
def compile_time_bucket(element: time_bucket, compiler, **kw):
    human_time = humanize_time(element.timestamp)
    name: str = element.name
    final_name = name
    if name not in ["event_at", "created_at", "updated_at"]:
        final_name = underscore(parameterize(humanize_time(name)))

    return f"time_bucket('{human_time}', {name}) AS {final_name}"


class create_uuid(FunctionElement):
    name = 'coalesce'


@compiles(create_uuid)
def compile(element, compiler, **kw):
    return "gen_random_uuid()"
