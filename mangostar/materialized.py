import random as rand
import uuid
from typing import Optional

from devtools import debug
from loguru import logger

from decorator import decorator
from pglast import parse_sql
from random_word import RandomWords
# from sqlalchemy import cast
from sqlalchemy import select
from sqlalchemy.dialects import postgresql as psql
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import DDLElement
from sqlalchemy.sql import ClauseElement
from sqlalchemyplus import CreateMaterializedView
from toolz import curry

from mangostar.circular import _init_tables
from mangostar.matches import FieldType
from mangostar.matches import MatchSQL
from mangostar.matches import TableType
from mangostar.pytables import *
from mangostar.tables import MetaTableAdapter

rand_words = RandomWords()
adapter = TableAdapter()
# meta_adapter: Optional[MetaTableAdapter] = None
# A local password for the time being.


class CreateView(DDLElement):
    def __init__(
        self,
        name,
        selectable,
    ):
        self.name = name
        self.selectable = selectable


@compiles(CreateView)
def compile_create_materialized_view(element, compiler, **kw):

    # Inserting these variables into the statement.
    name: str = element.name
    select_stmt: ClauseElement = compiler.sql_compiler.process(
        element.selectable, literal_binds = True
    )

    return f'CREATE MATERIALIZED VIEW IF NOT EXISTS {name} AS \n\t {select_stmt}'.format(
        name,
        compiler.sql_compiler.process(element.selectable, literal_binds = True),
    )


class DropView(DDLElement):
    def __init__(self, name, materialized = False, cascade = True):
        self.name = name
        self.materialized = materialized
        self.cascade = cascade


@compiles(DropView)
def compile_drop_materialized_view(element, compiler, **kw):
    return 'DROP VIEW IF EXISTS {} {}'.format(
        element.name, 'CASCADE' if element.cascade else ''
    )


@decorator
def compilize(func, *args, **kw):
    "Restrict access to a given class of users"

    fn: ClauseElement = func(*args, **kw)
    cmp = fn.compile(
        dialect = psql.dialect(), compile_kwargs = {"literal_binds": True}
    )
    return cmp


@curry
def json_col(field: FieldType, meta_adapter: MetaTableAdapter):
    name, kind = field.name, field.sql_type
    if field.parent_path:
        return meta_adapter.kernel.field_nest(name, field.parent_path, kind)
    return meta_adapter.kernel.field_as(name, kind)


def create_select(table: TableType, _adapter: MetaTableAdapter):
    if not table.field_count:
        raise ValueError(
            "We can't create a select function with zero fields. Again Later."
        )
    adapted_col = json_col(meta_adapter = _adapter)
    traits_gen = list(map(adapted_col, table.traits))
    traits_gen += _adapter.kernel.combined
    select_stmt = (
        select(traits_gen).where(_adapter.kernel.bucket == table.entity)
    )

    return select_stmt


@compilize
def build_view(table: TableType, _adapter: Optional[MetaTableAdapter] = None):
    _ladapter = _adapter or _init_tables()
    return CreateView(table.name, selectable = create_select(table, _ladapter))


@compilize
def create_materialized_view(table: TableType):
    """Creates a materialized view for a table .

    Args:
        table (TableType): Table nodes build from the dag.

    Returns:
        CreateMaterializedView: Create Materialized View.
    """
    return CreateMaterializedView(build_view(table))


# def
def gen_field():
    mark_of = rand.choice(['number', 'string', 'integer', 'boolean'])
    return {
        "item_id": uuid.uuid4().hex,
        "name": f"test_field_{uuid.uuid4().hex}",
        "attrs": {
            "node_type": "component",
            "sub_type": "field",
            "field_type": mark_of
        }
    }


def main():
    table_node_dict = {
        "item_id": uuid.uuid4().hex,
        "name": "test_int",
        "attrs": {
            "node_type": "entity",
            "sub_type": "tables",
        }
    }
    sql_match = MatchSQL(table_node_dict)
    table_node: TableType = sql_match.node
    for _ in range(10):
        tmp = MatchSQL(gen_field())
        table_node.add_field(tmp.node)

    # Building The First View
    built = build_view(table_node)
    logger.info(built)
    # hump = parse_sql(str(built))
    # debug(hump)


if __name__ == "__main__":
    main()
