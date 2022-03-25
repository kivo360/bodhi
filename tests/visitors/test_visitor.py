from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from bodhi_server import match_sql
from bodhi_server.matches import FieldType
from bodhi_server.matches import TableType
from bodhi_server.schema import TraversalManager


@pytest.fixture
def field_node():
    return {
        "item_id": "inside-0d5b80abb44c9568b39087f039ed1809",
        "name": "inside",
        "attrs": {
            "field_type": "integer",
            "node_type": "component",
            "sub_type": "field",
        },
    }


@pytest.fixture
def table_node():
    return {
        "item_id": "inside-0d5b80abb44c9568b39087f039ed1809",
        "name": "services",
        "attrs": {
            "node_type": "entity",
            "sub_type": "tables",
        },
    }


class TestTraversal:
    def test_match_field(self, field_node: dict):
        node = match_sql(field_node)
        assert isinstance(node, FieldType)

    def test_match_table(self, table_node: dict):
        node = match_sql(table_node)
        assert isinstance(node, TableType)

    # def test_match_field
