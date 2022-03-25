from typing import Any, Dict, List, Optional

from devtools import debug
from inflection import camelize
from inflection import tableize
from inflection import underscore
from loguru import logger

from pglast import prettify
from pydantic import validator
from toolz import curry

from bodhi_server import match_sql
from bodhi_server import Visitor
from bodhi_server.circular import _init_tables
from bodhi_server.core import FlexibleModel
from bodhi_server.main import Component
from bodhi_server.main import Entity
from bodhi_server.main import System
from bodhi_server.matches import TableType
from bodhi_server.materialized import build_view
from bodhi_server.schema import PrePostSplit
from bodhi_server.schema import TraversalManager


class TablesAndRels(FlexibleModel):
    tables: List[TableType] = []
    relationships: List[dict] = []
    path_list: List[str] = []

    def add_table(self, table: TableType):
        if len(self.tables) == 0:
            self.tables.append(table)
            return
        # is_table = is_table_id(table_id = table.item_id)
        # Going through a map to determine
        for tbl in self.tables:
            if tbl.item_id == table.item_id:
                if len(tbl.table_fields) < len(table.table_fields) or len(
                    tbl.parent_path
                ) < len(table.parent_path):
                    self.tables.remove(tbl)
                    self.tables.append(table)


class Field(Component):
    def __init__(self, field_type: str, aggregate: str = "sum", **attrs):
        super().__init__("field", **attrs)
        # aggregate = aggregate.upper()
        self.add_props(field_type=field_type)

    @property
    def field_type(self) -> str:
        return self.graph_repr.field_type

    def create(self, field_name: str):
        self._name = field_name
        return self


class Table(Entity):
    def __init__(self, table_name: str, **attrs):
        super().__init__("table", name=table_name, **attrs)


class SQLVisitor(Visitor):
    def __init__(self, _system: System):
        super().__init__(_system)
        self.traverser = TraversalManager(system=self.system)
        self.local_tables = {"tables": [], "relationships": []}
        self.local_tables_two = TablesAndRels()

    def node_split(self):
        curr_nodes = self.current_nodes
        split: PrePostSplit = self.traverser.pre_post_split(nodes=curr_nodes)
        topology = self.rev_top_sort
        return curr_nodes, split, topology

    def parents_set(self, child: str) -> Dict[str, Any]:
        return self.traverser.parents(child)

    def step(self):
        super().step()
        nodes, split, topology = self.node_split()
        for parent, children in nodes.items():
            _table = self.node(parent)
            for child in split.remove_post(children):
                _table.add_field(self.node(child))

    def node(self, n: str, parent_path: List[str] = []):
        return match_sql(
            {"item_id": n, "parent_path": parent_path, **self.system.get_node(n)}
        )

    def visit(self, _system: Optional[System] = None):
        if _system is not None:
            self.system = _system
        if not self.has_started:
            self.step()

        nodes, split, topology = self.node_split()
        for parent, children in nodes.items():
            if parent in split.post_nodes:
                continue
            child_table = self.node(parent)
            for child in split.remove_post(children):
                child_table.add_field(self.node(child))
            self.local_tables_two.tables.append(child_table)
            self.local_tables["tables"].append(child_table)

        sorted_topology = list(filter(lambda x: x in split.post_nodes, topology))
        for node_item in sorted_topology:
            # We're going to go about finding the root of the system.
            # We find the parents of the system here
            parent_child = self.traverser.parents(node_item)
            parents = parent_child.parents
            for parent in parents:
                relation = {"super": parent, "sub": node_item}
                self.local_tables["relationships"].append(relation)
                self.local_tables_two.relationships.append(relation)
            nested_child = self.traverser.children(node_item).children
            child_table = self.node(node_item, parent_path=parent_child.json_path)
            for _child in nested_child:
                if _child in sorted_topology:
                    continue
                child_table.add_field(self.node(_child, parent_child.json_path))

            self.local_tables["tables"].append(child_table)
            self.local_tables_two.tables.append(child_table)
        return self.local_tables_two


def plan_sql(dag_system: System) -> str:
    """Execute SQLAlchemy plan for the given Dag system .

    Args:
        dag_system (System): Use dag system to generate SQLAlchemy code.
    """
    _base_table_adapter = _init_tables()
    sql_planner: SQLVisitor = SQLVisitor(dag_system)
    table_and_rels = sql_planner.visit()

    table_set, relation_set = table_and_rels.tables, table_and_rels.relationships
    sql_commands = []
    for table in table_set:
        _table = build_view(table, _base_table_adapter)
        sql_commands.append(_table)

    for _table in sql_commands:
        logger.warning(prettify(str(_table)))

    logger.debug(relation_set)
    return sql_commands
