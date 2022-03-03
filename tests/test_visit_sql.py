from typing import Dict, List

from devtools import debug
from inflection import camelize
from inflection import tableize
from inflection import underscore
from loguru import logger

import more_itertools as mtoolz
import pytest

from mangostar import SQLVisitor
from mangostar import System

# logger.disable(__file__)


@pytest.mark.parametrize('field_nums', [2, 3])
def test_vistor_has_started(flat_table: System):
    sql_visitor = SQLVisitor(flat_table)
    assert not sql_visitor.has_started

    sql_visitor.step()

    assert sql_visitor.has_started


@pytest.mark.parametrize('field_nums', [2, 3, 10])
def test_get_root_node(flat_table: System):
    sql_visitor = SQLVisitor(flat_table)
    nodes: Dict[str, List[str]] = sql_visitor.current_nodes
    logger.debug(nodes)
    assert len(nodes) > 0


@pytest.mark.parametrize('field_nums', [2, 3])
def test_get_table_fields(flat_table: System, field_nums: int):

    visitor = SQLVisitor(flat_table)
    logger.warning(visitor.num_nodes)
    visitor.step()
    assert visitor.has_children
    assert visitor.num_children == field_nums

    visitor.update_switch()
    visitor.step()

    assert not visitor.has_children


@pytest.mark.parametrize('field_nums', [2, 3, 5])
def test_nested_table(nested_table: System, field_nums: int):

    visitor = SQLVisitor(nested_table)
    tables_and_relations = visitor.visit()
    # debug(tables_and_relations)
    # Is there at least one relationship?
    assert len(tables_and_relations.relationships) > 0
