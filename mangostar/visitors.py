from typing import Callable, Optional, Union

from mangostar import Array
from mangostar import Entity
from mangostar import Field
from mangostar import JsonSchemaParents
from mangostar import JsonSchemaTypes
from mangostar import Nested
from mangostar import Scalar
from mangostar import system
from mangostar import Table
from mangostar import Top

OptParent = Optional[JsonSchemaParents]
# 'number', 'string', 'integer', 'boolean'
FIELD_MAP = {
    "integer": Field("integer"),
    "number": Field("number"),
    "string": Field("string"),
    "boolean": Field("boolean"),
}


def visit_json(
    json_value: JsonSchemaTypes,
    parent: Optional[JsonSchemaParents] = None,
) -> Union[Table, Field]:
    fn_name: str = f"visit_json_{json_value.cls_name}"
    func: Callable[[JsonSchemaTypes, OptParent],
                   JsonSchemaTypes] = globals().get(fn_name)
    return func(json_value, parent)


def add_to_sys(
    table: Table,
    parent: JsonSchemaTypes = None,
    edge_type: str = "related_to",
):
    if parent:
        init_parent = visit_json(parent)
        # TODO: Figure out where to get edge properties from
        init_parent.add(table, edge_type = edge_type)
    else:
        loc_sys = system()
        loc_sys.add(table)


def visit_json_scalar(
    json_value: Scalar, parent: Optional[JsonSchemaTypes] = None
):
    init_parent = visit_json(parent)
    field = FIELD_MAP.get(json_value.item_type).create(json_value.field_name)
    init_parent.add(field, edge_type = "field_of")
    return field


def visit_json_array(
    json_value: Array,
    parent: Optional[JsonSchemaTypes] = None,
):
    table = Table(json_value.field_name)
    add_to_sys(table, parent)
    return table


def visit_json_nested(
    json_value: Nested,
    parent: Optional[JsonSchemaTypes] = None,
) -> Table:
    table = Table(json_value.field_name)
    add_to_sys(table, parent)
    return table


def visit_json_top(
    json_value: Top,
    parent: Optional[JsonSchemaTypes] = None,
) -> Table:
    table = Table(json_value.field_name)
    add_to_sys(table, parent)
    return table


class Table(Entity):
    def __init__(self, table_name: str, **attrs):
        super().__init__("table", name = table_name, **attrs)
