import re
import sys
from datetime import datetime
from logging import log
from typing import Any, List, Optional

from loguru import logger

from pydantic import validate_arguments
from sqlalchemy.sql.expression import false
from stringcase import snakecase

from mangostar import connection
from mangostar import circular as circle

from mangostar.circular import _init_tables
from mangostar.circular import DBResponse
from mangostar.convert import json_to_sql
from mangostar.graph_database.graph import ViewParams
from mangostar.logic.maestro import NameMaestro
from mangostar.settings import ModuleSettings
from mangostar.tables import MetaTableAdapter
from fastapi import HTTPException

# A bunch of models for saving information
from mangostar.models import Measurement, MeasureSet

adapter: Optional[MetaTableAdapter] = None
settings = ModuleSettings()
NAME_CONTROLLER: NameMaestro = NameMaestro()


# logger.configure(
#     handlers=[
#         dict(sink=sys.stdout, serialize=True),
#         dict(sink=sys.stderr, serialize=True),
#     ],
# )


def get_db():
    return connection.relational


def normalize_data(inputs: dict):
    if not isinstance(inputs, dict):
        return inputs
    resp = {}
    for key, value in inputs.items():
        norm_key = snakecase(key)
        if isinstance(value, dict):
            resp[norm_key] = normalize_data(value)
            continue
        elif isinstance(value, list):
            if not value:
                resp[norm_key] = []
                continue
            resp[norm_key] = list(map(normalize_data, value))
            continue
        elif isinstance(value, str):
            conv = value.encode().decode("unicode-escape", errors="ignore")
            # conv.replace('')
            resp[norm_key] = conv
        resp[norm_key] = value
    return resp


@validate_arguments
def insert_dict(
    *,
    bucket: str,
    tags: dict = {},
    event_at: datetime = datetime.now(),
    data: dict = {},
    **values
):
    # IRL, this will be sent to another serverless function
    database = connection.relational

    norm_dict = normalize_data(data)
    try:
        database.kernel.insert_into(
            is_execute=True, bucket=bucket, tags=tags, event_at=event_at, data=norm_dict
        )

    except Exception as e:
        # logger.exception(e)
        return (
            DBResponse(
                status=False, message="Failed to add record somewhere along the way."
            ),
            500,
        )

    created_views = create_new_view(bucket, data)
    if not created_views:
        return DBResponse(
            status=True,
            data={},
            message="Data was added. No need to create a new schema.",
        )
    try:
        for view in created_views:
            view_str: str = str(view)
            adapter.engine.execute(view_str)
    except Exception as e:
        logger.exception(e)
        logger.info(str(e))
        return DBResponse(
            status=False,
            data={},
            message="Data was added. No need to create a new schema.",
        )

    return DBResponse(status=True, message="Successfully added message"), 201


def create_new_view(bucket: str, data: dict):
    created_views: List[Any] = NAME_CONTROLLER.update_schema(
        view_name=bucket, record=data, view_space=ViewParams(**settings.ns_dict)
    )
    return created_views


def execute_view(created_views: List[Any]):
    database = connection.relational
    try:
        for view in created_views:
            view_str: str = str(view)
            database.engine.execute(view_str)
        return 200, "Views created"
    except Exception as e:
        logger.exception(e)
        return 500, "Views created"


@validate_arguments
def ingest_data(
    *,
    bucket: str,
    tags: dict = {},
    event_at: datetime = datetime.now(),
    data: dict = {},
    **values
):
    # NOTE: This should most certainly not be global now that I think about it.
    # There are better options.
    # TODO: Replace your damn values
    database = connection.relational
    norm_dict = normalize_data(data)
    try:
        response = database.kernel.insert_into(
            is_execute=True, bucket=bucket, tags=tags, event_at=event_at, data=norm_dict
        )
        logger.warning(response)
    except Exception as e:
        logger.exception(e)
        response_message = "The data was not added to the database"
        return DBResponse(status=False, data={}, message=response_message)

    return DBResponse(status=True, data={}, message="Success")


def find(*, bucket: str, tags: dict = {}, **values):
    pass


def refresh_view(*, bucket: str, tags: dict = {}):
    pass


def create_materialized_view(
    *, data: dict, bucket: Optional[str] = None, indexing_tag: Optional[dict] = {}
):
    pass


def measure_one(measure: Measurement):
    pass


def measure_many(measure_set: MeasureSet):
    try:
        db = get_db()
        db.metrics.insert_many(measure_set.get_insertable())
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500, detail="Unable to save the specific metrics"
        )


if __name__ == "__main__":
    json_to_sql({"hello": "world", "eat": {"tons": "of shit"}}, "playground")
