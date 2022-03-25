import random as rand
import uuid
from typing import Generator

from inflection import underscore

import pytest
from faker import Faker
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text

from bodhi_server.matches import FieldType
from bodhi_server.matches import MatchSQL
from bodhi_server.matches import TableType
from bodhi_server.utils import consistent_naming as const_name


def _generate_field(name: str, field_type: str):
    return {
        "item_id": uuid.uuid4().hex,
        "name": f"test_field_{field_type}_{name}",
        "attrs": {
            "node_type": "component",
            "sub_type": "field",
            "field_type": field_type,
        },
    }


@pytest.fixture
def generate_field(field_type: str):
    return _generate_field(uuid.uuid4().hex, field_type)


def random_field_nodes(
    local_faker: Faker, record_number: int = 1
) -> Generator[dict, None, None]:

    for _ in range(record_number):
        company_name = local_faker.company()
        yield _generate_field(
            const_name(company_name),
            rand.choice(["number", "string", "integer", "boolean"]),
        )


@pytest.fixture
def random_table_node(core_faker: Faker):
    crypto_name = core_faker.cryptocurrency_name()
    return {
        "item_id": uuid.uuid4().hex,
        "name": const_name(crypto_name),
        "attrs": {
            "node_type": "entity",
            "sub_type": "tables",
        },
    }


class TestSqlMatchAndComposition:
    @pytest.mark.parametrize(
        "field_type, expected",
        [
            ("integer", Integer),
            ("string", Text),
            ("boolean", Boolean),
            ("number", Numeric),
        ],
    )
    def test_fields(self, generate_field, expected):
        sql_matcher = MatchSQL(generate_field)
        assert sql_matcher.is_sql
        node = sql_matcher.get_node()
        assert isinstance(node, FieldType)
        assert node.sql_type == expected

    def test_table_match(self):
        table_node = {
            "item_id": uuid.uuid4().hex,
            "name": "test_int",
            "attrs": {
                "node_type": "entity",
                "sub_type": "tables",
            },
        }
        sql_matcher = MatchSQL(table_node)
        assert sql_matcher.is_sql
        node = sql_matcher.get_node()
        assert isinstance(node, TableType)

    @pytest.mark.parametrize("record_number", [5, 10, 25])
    def test_table_proper_size(
        self,
        record_number: int,
        random_table_node: dict,
        core_faker: Faker,
    ):
        sql_matcher = MatchSQL(random_table_node)
        assert sql_matcher.is_sql

        # -----------------------------------------------------
        # -----------------------------------------------------
        assert isinstance(sql_matcher.node, TableType)

        table_plan: TableType = sql_matcher.node

        for field_dict in random_field_nodes(core_faker, record_number=record_number):
            field_matcher = MatchSQL(field_dict)
            assert field_matcher.is_sql
            field = field_matcher.node
            table_plan.add_field(field)

        assert table_plan.field_count == record_number

    @pytest.mark.parametrize("record_number", [5])
    def test_call_sql_select_statement(
        self,
        record_number: int,
        random_table_node: dict,
        core_faker: Faker,
    ):
        sql_matcher = MatchSQL(random_table_node)
        assert sql_matcher.is_sql

        # -----------------------------------------------------
        # -----------------------------------------------------
        assert isinstance(sql_matcher.node, TableType)

        table_plan: TableType = sql_matcher.node

        for field_dict in random_field_nodes(core_faker, record_number=record_number):
            field_matcher = MatchSQL(field_dict)
            assert field_matcher.is_sql
            field = field_matcher.node
            table_plan.add_field(field)

        assert table_plan.field_count == record_number
