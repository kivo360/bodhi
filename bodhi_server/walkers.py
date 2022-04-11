# from typing import List, Literal, Optional, Union

from typing import cast, Optional

from inflection import underscore
from loguru import logger

from bodhi_server import ConstrNum
from bodhi_server import get_schema
from bodhi_server import is_array
from bodhi_server import is_nested
from bodhi_server import is_scalar
from bodhi_server import is_top
from bodhi_server import JsonSchemaTypes
from bodhi_server import Scalar
from bodhi_server import system
from bodhi_server import visit_json
from bodhi_server.typinger import DictStrAny


@logger.catch(reraise=True)
def schema_walk(
    js_schema: DictStrAny,
    name: str,
    parent: Optional[JsonSchemaTypes] = None,
    system_id: Optional[str] = None,
):
    """Walk the JSON Schema and recursively walk through the JSON Schema .

    Args:
        js_schema (DictStrAny): The dictionary schema that we're scanning through.
        name (str): The name of the element.
        parent (Optional[JsonSchemaTypes], optional): The parent node that we're aiming to scan through. This is to add to the networkx. Defaults to None.

    Raises:
        ValueError: Raises if the json schema is empty.

    """

    if not js_schema:
        raise ValueError("The JSONSchema is empty")

    field = get_schema(js_schema)
    field.field_name = name

    _is_top = is_top(field)
    _is_nested = is_nested(field)

    if _is_top or _is_nested:

        logger.info(
            f"""
            It is the top: {_is_top},
            Is Nested: {_is_nested}
        """
        )

        if not field.has_props:

            return {}
        visit_json(field, parent)

        for key, value in field.properties.items():
            schema_walk(
                js_schema=value,
                name=key,
                parent=field,
            )

    elif is_array(field) and parent is not None:
        visit_json(field, parent)
        child = get_schema(field.items)

        schema_walk(
            js_schema=field.items,
            name=child.field_name,
            parent=field,
        )

    elif is_scalar(field) and parent is not None:
        if isinstance(field, ConstrNum):
            field = cast(ConstrNum, field)
            field: "Scalar" = field.to_scalar()
        visit_json(field, parent)
    else:
        logger.error(
            "None of the proper conditions were met. We can't add a scalar or an array without a parent. Reason for"
        )


def standardize_naming(jsonschema_dict: dict):
    if not isinstance(jsonschema_dict, dict):
        return jsonschema_dict

    standardized = {}
    for key, value in jsonschema_dict.items():
        _key = underscore(key)
        if isinstance(value, dict):

            if len(value) > 0:
                standardized[_key] = standardize_naming(value)
            else:
                standardized[_key] = {}
        elif isinstance(value, list):
            standardized[_key] = []
            if len(value) > 0:
                standardized[_key].append(standardize_naming(value))
        else:
            standardized[_key] = value

    return standardized


if __name__ == "__main__":
    root_table_name = "root_table"
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
    # local_schema = standardize_naming(local_schema)
    schema_walk(local_schema, root_table_name)
    global_system = system()
    global_system_dict = global_system.to_dict()
    relationships = filter(lambda x: "adjacencies" in x, global_system_dict)
    logger.warning(len(list(relationships)))
    logger.info(global_system.net)
