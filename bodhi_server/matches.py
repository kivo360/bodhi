from typing import Generator, List, Literal, Optional, Union

from inflection import underscore

from addict import Addict
from pydantic import BaseModel
from pydantic import conlist
from pydantic import Field
from pydantic import root_validator
from sqlalchemy import Boolean
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import Text


class SchemaField(BaseModel):
    item_type: str = Field(alias = "type")
    field_name: Optional[str] = None

    class Config:
        extra = 'allow'
        arbitrary_types_allowed = 'allow'

    @property
    def cls_name(self):
        return underscore(self.__class__.__name__)


class FieldWithProps(SchemaField):
    item_type: Literal['object'] = Field(alias = "type")
    properties: dict
    required: Optional[List[str]] = []

    @property
    def num_props(self) -> int:
        return len(self.properties)

    @property
    def has_req(self) -> bool:
        return bool(self.required)

    @property
    def has_props(self) -> bool:
        """Whether this node has any properties .

        Returns:
            bool: If properties exists.
        """
        return len(self.properties) > 0


class Top(FieldWithProps):
    top_schema: str = Field(alias = "$schema")


class Nested(FieldWithProps):
    pass


class Array(SchemaField):
    item_type: Literal['array'] = Field(alias = "type")
    items: dict


class Scalar(SchemaField):
    item_type: Literal['number', 'string', 'integer',
                       'boolean'] = Field(alias = "type")


class Number(SchemaField):
    item_type: Literal['number', 'integer'] = Field(alias = "type")


class ConstrNum(FieldWithProps):
    _min: Number = Field(alias = "min")
    _max: Number = Field(alias = "max")
    required: conlist(str, min_items = 2, max_items = 2)

    def to_scalar(self):
        return Scalar(type = "number", field_name = self.field_name)


class Searched(BaseModel):
    current_field: Union[Top, ConstrNum, Nested, Array, Scalar]


class SearchTables(BaseModel):
    current_field: Union[Top, ConstrNum, Nested, Array, Scalar]


class NodeAttrs(BaseModel):
    node_type: str
    sub_type: Optional[Literal['field', 'tables']] = None
    field_type: Optional[str] = None


class SqlBaseModel(BaseModel):
    item_id: str
    name: str
    attrs: NodeAttrs
    parent_path: Optional[List[str]] = []


class SQLType(BaseModel):
    item_id: str
    name: str
    parent_path: Optional[List[str]] = []
    entity: Optional[str] = None

    @root_validator
    def sets_entity_value(cls, values):
        """Sets the entity value for the given list of values .

        Args:
            values (dict): All of the models values.

        Returns:
            dict: THe modified values. 
        """
        validator_getter_dict = Addict(**values)
        parents = validator_getter_dict.parent_path
        if len(parents) > 0:
            validator_getter_dict.entity = parents[0]
            return validator_getter_dict.to_dict()
        validator_getter_dict.entity = validator_getter_dict.name
        return validator_getter_dict.to_dict()


class FieldType(SQLType):

    field_type: Literal['number', 'string', 'integer', 'boolean']

    @property
    def is_parent(self) -> bool:
        return len(self.parent_path) > 0

    @property
    def top_level_json_entity(self):
        return self.parent_path[0]

    @property
    def sql_type(self):
        return {
            "string": Text,
            "integer": Integer,
            "boolean": Boolean,
            "number": Numeric
        }[self.field_type]

    def __str__(self):
        return super().__repr__()


class TableType(SQLType):
    table_fields: List[FieldType] = []

    @property
    def field_count(self) -> int:
        return len(self.table_fields)

    @property
    def traits_generator(self) -> Generator[FieldType, None, None]:
        for trait in self.table_fields:
            yield trait

    @property
    def traits(self):
        for trait in self.table_fields:
            yield trait

    def add_field(self, field: FieldType):
        self.table_fields.append(field)


class MatchSQL:
    def __init__(self, value: dict):
        self.is_sql: bool = False
        self.model: SqlBaseModel = None
        try:
            self.model = SqlBaseModel(**value)
            self.is_sql = True
        except Exception:
            pass

    def is_valid(self) -> bool:
        return self.is_sql

    def get_node(self) -> Union[FieldType, TableType]:
        if not self.is_sql:
            raise ValueError("The node is not a valid sql node.")
        exact_type = self.model.attrs.sub_type
        if exact_type == "tables":
            return TableType(
                item_id = self.model.item_id,
                name = self.model.name,
                parent_path = self.model.parent_path
            )

        return FieldType(
            item_id = self.model.item_id,
            name = self.model.name,
            field_type = self.model.attrs.field_type,
            parent_path = self.model.parent_path
        )

    @property
    def node(self):
        return self.get_node()


def get_sql_nodes(value_dict: dict) -> Union[FieldType, TableType]:
    matcher = MatchSQL(value_dict)
    return matcher.get_node()


def get_field_type(value_dict: dict) -> Union[Nested, Array, Scalar, Top]:
    """Returns a field type based on the value_dict .

    Args:
        value_dict (dict): [description]

    Returns:
        Union[Nested, Array, Scalar, Top]: One of teh Field Types
    """
    return Searched(current_field = value_dict).current_field


JsonSchemaTypes = Union[Top, ConstrNum, Nested, Array, Scalar]
JsonSchemaParents = Union[Top, Nested, Array]


def is_top(item: JsonSchemaTypes) -> bool:
    """Returns True if the given schema is a top level json schema.

    Args:
        item (JsonSchemaTypes): One of the schema types.

    Returns:
        bool: True if item is a top level json schema.
    """
    return isinstance(item, Top)


def is_nested(item: JsonSchemaTypes) -> bool:
    """Returns True if the given item is a Nested type .

    Args:
        item (JsonSchemaTypes): One of the different kinds of values.

    Returns:
        bool: True if item is a Nested type.
    """
    return isinstance(item, Nested)


def is_array(item: JsonSchemaTypes) -> bool:
    """Returns True if the item is an array node .

    Args:
        item (JsonSchemaTypes): [description]

    Returns:
        [type]: [description]
    """
    return isinstance(item, Array)


def is_scalar(item: JsonSchemaTypes) -> bool:
    """Returns true if the item is a scalar .

    Args:
        item (JsonSchemaTypes): One of the types. 

    Returns:
        bool: [description]
    """
    return isinstance(item, (Scalar, ConstrNum))
