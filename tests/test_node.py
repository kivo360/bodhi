import re
from typing import List

from loguru import logger

from bodhi_server import Component
from bodhi_server import Entity
from bodhi_server import Subsystem
from bodhi_server import System

MD5_REG = r"([a-fA-F\d]{32})"


def split_node_id(node_id: str) -> List[str]:
    return node_id.split("-")


def is_md5(hashed_str: str) -> bool:
    return bool(re.findall(MD5_REG, hashed_str))


def test_node_id():
    # This is how a table is technically configured internally. Therefore we're going to label it like this.
    # In next steps, nodes will also have something stating the first node it belongs to.
    # This will be the case until we can put it into a graph database (fingers crossed)
    test_entity = Entity("table", name="test_table_name")
    n_id: str = test_entity.node_id
    separated = split_node_id(n_id)

    # Check if there's a table name and a unique md5 hash
    assert len(separated) == 2
    assert is_md5(separated[1])


def test_add_entity(dynamic_system: System):
    table = Entity("table", name="test_table_name")
    # Adding to the tests' system
    table.add_current(dynamic_system)
    assert dynamic_system.node_count > 0


def test_add_component_to_entity(dynamic_system: System):
    table = Entity("table", name="test_table_name")
    table.system = dynamic_system
    # Adding to the tests' system
    table_attr = Component("field", "test_field_name")
    table.add(table_attr)
    assert dynamic_system.node_count == 2
    assert dynamic_system.edge_count == 1
    assert dynamic_system.root_id
