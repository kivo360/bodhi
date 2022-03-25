from functools import cached_property
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean
from sqlalchemy import cast
from sqlalchemy import Column
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import NUMERIC
from sqlalchemy import select as _select
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.schema import Index
from sqlalchemy.sql.selectable import TableClause
from sqlalchemy.types import TypeEngine
from sqlalchemy.engine import Engine

from bodhi_server.timescale import create_uuid


def select(*args, **kwargs):
    return _select(args, **kwargs)


class BaseWrapper(object):
    def __init__(self, table: TableClause):
        self._table = table

    @property
    def table(self):
        return self._table

    @cached_property
    def conn(self) -> Engine:
        return self._table.bind

    def execute(self, *args, **kwargs):
        return self.conn.execute(*args, **kwargs)

    def insert_into(self, is_execute: bool = False, **values):
        insert_query = self.table.insert().values(**values)
        if is_execute:
            insert_query.execute()
        return insert_query

    def insert_many(self, values: List[Dict[str, Any]]):
        """Insert Many Values. Running execute is inherient"""
        self.execute(self.table.insert(), values)


def create_nested_path(nested_list: list, element: str):
    composite = "$"
    for i in nested_list:
        composite += f".{i}[*]"
    return f"{composite}.{element}"


class KernelWrapper(BaseWrapper):
    def field_as(self, name: str, field_type: TypeEngine):
        return cast(self.table.c.data[name].astext, field_type).label(name)

    def field_nest(self, name, name_path: List[str], field_type: TypeEngine):
        if len(name_path) < 2:
            raise ValueError("You should have multiple string fields.")
        return cast(
            func.jsonb_path_query(
                self.table.c.data, create_nested_path(name_path, name)
            ),
            field_type,
        ).label(name)

    @property
    def data(self):
        return self.table.c.data

    @property
    def c(self):
        return self.table.c

    @property
    def event_at_col(self):
        return self.table.c.event_at.label("event_at")

    @property
    def created_at_col(self):
        return self.table.c.created_at.label("created_at")

    @property
    def tags_at_col(self):
        return self.table.c.tags.label("tags")

    @property
    def combine_select_list(self):
        return [self.tags_at_col, self.created_at_col, self.event_at_col]

    @property
    def combined(self):
        return [self.tags_at_col, self.created_at_col, self.event_at_col]

    @property
    def bucket(self):
        return self.table.c.bucket


class MetaTableAdapter:
    def __init__(self, metadata: Optional[MetaData] = None):
        self.metadata = metadata or MetaData()
        self.load_tables()
        self.engine: Engine = self.metadata.bind

    def load_tables(self):
        """Loads the tables for the first time. For cache purposes."""
        self.kernel
        self.clock
        self.event_log
        self.episode
        self.session
        self.mappings
        self.metrics

    @cached_property
    def kernel(self):

        _kernel = Table(
            "kernel",
            self.metadata,
            Column(
                "kernel_id",
                UUID(as_uuid=True),
                primary_key=True,
                unique=True,
                nullable=False,
                server_default=create_uuid(),
            ),
            Column("data", JSONB, default={}),
            Column("tags", JSONB, default={}),
            Column("bucket", TEXT, nullable=False),
            Column(
                "event_at",
                TIMESTAMP(timezone=True),
                nullable=False,
                server_default=func.current_timestamp(),
            ),
            Column(
                "created_at",
                TIMESTAMP(timezone=True),
                nullable=False,
                server_default=func.current_timestamp(),
            ),
        )
        """ Creating Indexes Here. """
        Index("ix_json", _kernel.c.data, _kernel.c.tags, postgresql_using="gin")
        Index("ix_time", _kernel.c.created_at, _kernel.c.event_at)
        Index("idx_buck", _kernel.c.bucket)

        return KernelWrapper(_kernel)

    """
        Getting to these after MVP.
    """

    @cached_property
    def clock(self):
        return Table(
            "clock",
            self.metadata,
            Column(
                "id",
                UUID(as_uuid=True),
                server_default=create_uuid(),
                primary_key=True,
                unique=True,
                nullable=False,
            ),
            Column("step_size", NUMERIC, default=1, nullable=False),
            Column("window_size", Integer, default=1, nullable=False),
            Column("head", TIMESTAMP(timezone=False), nullable=False),
            Column("tail", TIMESTAMP(timezone=False), nullable=False),
            Column("y_size", Integer, default=1, nullable=False),
            Column("y_pred", TIMESTAMP(timezone=False), nullable=False),
        )

    @cached_property
    def episode(self):
        episode_table = Table(
            "episode",
            self.metadata,
            Column(
                "id",
                UUID(as_uuid=True),
                primary_key=True,
                unique=True,
                nullable=False,
            ),
            Column("session_id", NUMERIC, default=1, nullable=False),
            Column("start", TIMESTAMP(timezone=True), nullable=False),
            Column("end", TIMESTAMP(timezone=True), nullable=False),
            Column("is_finished", Integer, default=1, nullable=False),
        )
        return episode_table

    @cached_property
    def session(self):
        return Table(
            "sessions",
            self.metadata,
            Column(
                "id",
                UUID(as_uuid=True),
                primary_key=True,
                unique=True,
                nullable=False,
            ),
            Column("num_episodes", Integer, default=0, nullable=False),
            Column("is_finished", Boolean, default=False, nullable=False),
        )

    @cached_property
    def mappings(self):
        return Table(
            "mappings",
            self.metadata,
            Column(
                "id", UUID(as_uuid=True), primary_key=True, unique=True, nullable=False
            ),
            Column("key_name", String, default=1, nullable=False),
            Column("key_id", String, nullable=False),
            Column("value_name", String, default=1, nullable=False),
            Column("value_type", String, nullable=False),
        )

    @cached_property
    def event_log(self):

        _kernel = Table(
            "event_log",
            self.metadata,
            Column(
                "event_id",
                UUID(as_uuid=True),
                primary_key=True,
                unique=True,
                nullable=False,
                server_default=create_uuid(),
            ),
            Column("data", JSONB, default={}),
            Column("tags", JSONB, default={}),
            Column("objects", JSONB, default={}),  # The omap of the objects
            Column("activity", TEXT, nullable=False),
            Column(
                "event_at",
                TIMESTAMP(timezone=True),
                nullable=False,
                server_default=func.current_timestamp(),
            ),
            Column(
                "created_at",
                TIMESTAMP(timezone=True),
                nullable=False,
                server_default=func.current_timestamp(),
            ),
        )
        """ Creating Indexes Here. """

        return KernelWrapper(_kernel)

    @cached_property
    def metrics(self):
        return KernelWrapper(
            Table(
                "metrics",
                self.metadata,
                Column(
                    "id",
                    UUID(as_uuid=True),
                    server_default=create_uuid(),
                    primary_key=True,
                    unique=True,
                    nullable=False,
                ),
                # the subject we're saving for.
                Column("subject", String, default=1, nullable=False),
                # The metric's name and values
                Column("name", String, default=1, nullable=False),
                # We'll be converting the value to string before saving
                Column("value", String, default=1, nullable=False),
                Column("val_type", String, default=1, nullable=False),
                # The time the simulation vs the actual time we've recorded it
                Column("clock_at", NUMERIC, default=1, nullable=False),
                Column("created_at", NUMERIC, default=1, nullable=False),
            )
        )

    def execute(self, statement, *args, **kwargs):
        self.engine.execute(statement, *args, **kwargs)
