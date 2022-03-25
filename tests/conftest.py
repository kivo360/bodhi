import random as rand
from uuid import uuid4

from loguru import logger

from faker import Faker
from pytest import fixture

from bodhi_server import Field
from bodhi_server import Subsystem
from bodhi_server import System
from bodhi_server import system
from bodhi_server import Table

fake = Faker()

FIELD_TYPES = ["integer", "boolean", "number", "string"]


def get_field() -> Field:
    return Field(rand.choice(FIELD_TYPES))


def _flat_table(field_nums: int, dynamic_system: System) -> Table:
    table_name = fake.word()
    field_names = fake.words(field_nums)
    table = Table(table_name)
    table.add_current(dynamic_system)
    for field_name in field_names:
        field = get_field()
        field.create(field_name)
        table.add(field)
    return table


@fixture
def dynamic_system() -> "System":
    return system(uuid4().hex)


@fixture
def flat_table(field_nums: int, dynamic_system: "System"):
    """Create a flat table from field number of fields .

    Args:
        field_nums (int): The number of fields we'd like to create.
        dyn_system (System): A dynamically generated system (from the module)

    Returns:
        System: The system we're adding the nodes and edges to.
    """
    _flat_table(field_nums, dynamic_system)
    return dynamic_system


@fixture
def nested_table(field_nums: int, dynamic_system: "System"):
    """Generate a table for a table .

    Args:
        field_nums (int): The number of fields a table is to have.
        dyn_system (System): Assumed the system exists as it's supposed to.

    Returns:
        [type]: [description]
    """

    table = _flat_table(field_nums, dynamic_system)
    random_children_count: int = rand.randint(1, 4)
    for _ in range(random_children_count):
        table.add(_flat_table(rand.randint(1, 4), dynamic_system))
    return dynamic_system


@fixture(scope="session")
def nested_jsonschema():
    local_schema = {
        "$schema": "http://json-schema.org/schema#",
        "type": "object",
        "properties": {
            "tierBased": {"type": "boolean"},
            "taker": {"type": "number"},
            "maker": {"type": "number"},
            "precision": {
                "type": "object",
                "properties": {
                    "base": {"type": "integer"},
                    "quote": {"type": "integer"},
                    "amount": {"type": "integer"},
                    "price": {"type": "integer"},
                },
                "required": ["amount", "base", "price", "quote"],
            },
            "limits": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "object",
                        "properties": {
                            "min": {"type": "number"},
                            "max": {"type": "number"},
                        },
                        "required": ["max", "min"],
                    },
                    "price": {
                        "type": "object",
                        "properties": {
                            "min": {"type": "number"},
                            "max": {"type": "number"},
                        },
                        "required": ["max", "min"],
                    },
                    "cost": {
                        "type": "object",
                        "properties": {
                            "min": {"type": "number"},
                            "max": {"type": "null"},
                        },
                        "required": ["max", "min"],
                    },
                    "market": {
                        "type": "object",
                        "properties": {
                            "min": {"type": "number"},
                            "max": {"type": "number"},
                        },
                        "required": ["max", "min"],
                    },
                },
                "required": ["amount", "cost", "market", "price"],
            },
            "id": {"type": "string"},
            "lowercaseId": {"type": "string"},
            "symbol": {"type": "string"},
            "base": {"type": "string"},
            "quote": {"type": "string"},
            "baseId": {"type": "string"},
            "quoteId": {"type": "string"},
            "info": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "status": {"type": "string"},
                    "baseAsset": {"type": "string"},
                    "baseAssetPrecision": {"type": "integer"},
                    "quoteAsset": {"type": "string"},
                    "quotePrecision": {"type": "integer"},
                    "quoteAssetPrecision": {"type": "integer"},
                    "baseCommissionPrecision": {"type": "integer"},
                    "quoteCommissionPrecision": {"type": "integer"},
                    "orderTypes": {"type": "array", "items": {"type": "string"}},
                    "icebergAllowed": {"type": "boolean"},
                    "ocoAllowed": {"type": "boolean"},
                    "quoteOrderQtyMarketAllowed": {"type": "boolean"},
                    "isSpotTradingAllowed": {"type": "boolean"},
                    "isMarginTradingAllowed": {"type": "boolean"},
                    "filters": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "filterType": {"type": "string"},
                                "minPrice": {"type": "string"},
                                "maxPrice": {"type": "string"},
                                "tickSize": {"type": "string"},
                                "multiplierUp": {"type": "string"},
                                "multiplierDown": {"type": "string"},
                                "avgPriceMins": {"type": "integer"},
                                "minQty": {"type": "string"},
                                "maxQty": {"type": "string"},
                                "stepSize": {"type": "string"},
                                "minNotional": {"type": "string"},
                                "applyToMarket": {"type": "boolean"},
                                "limit": {"type": "integer"},
                                "maxNumOrders": {"type": "integer"},
                                "maxNumAlgoOrders": {"type": "integer"},
                            },
                            "required": ["filterType"],
                        },
                    },
                    "permissions": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "baseAsset",
                    "baseAssetPrecision",
                    "baseCommissionPrecision",
                    "filters",
                    "icebergAllowed",
                    "isMarginTradingAllowed",
                    "isSpotTradingAllowed",
                    "ocoAllowed",
                    "orderTypes",
                    "permissions",
                    "quoteAsset",
                    "quoteAssetPrecision",
                    "quoteCommissionPrecision",
                    "quoteOrderQtyMarketAllowed",
                    "quotePrecision",
                    "status",
                    "symbol",
                ],
            },
            "margin": {"type": "boolean"},
            "future": {"type": "boolean"},
            "percentage": {"type": "boolean"},
            "type": {"type": "string"},
            "spot": {"type": "boolean"},
            "delivery": {"type": "boolean"},
            "active": {"type": "boolean"},
        },
        "required": [
            "base",
            "baseId",
            "future",
            "id",
            "info",
            "limits",
            "lowercaseId",
            "maker",
            "margin",
            "precision",
            "quote",
            "quoteId",
            "symbol",
            "taker",
            "tierBased",
        ],
    }
    return local_schema
