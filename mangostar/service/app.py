from datetime import datetime
from typing import Any, Dict, Optional

from devtools import debug
from inflection import tableize
from loguru import logger

from addict import Addict as DDict
from fastapi import FastAPI, Response
from pydantic import BaseModel
from pydantic import root_validator
from mangostar import commands, models
from mangostar import circular as circle
from mangostar import settings
from mangostar.circular import DBResponse, _init_tables
from mangostar.settings import ModuleSettings
from mangostar.utils import InsertParameters


settings_root = ModuleSettings()

app = FastAPI()


@app.on_event("startup")
async def start_databases():
    # logger.info(settings.postgres_connection_str)
    table = circle.init()
    logger.error(settings_root.postgres_connection_str)
    logger.info(table)


@app.get("/")
def read_root():
    sett = ModuleSettings()
    debug(sett.arangoo)
    debug(sett.postgres)
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.post("/insert", response_model=DBResponse)
def insert_item(item: InsertParameters):
    return commands.ingest_data(**item.dict())


@app.post("/measure")
def record_measurement(measurements: models.MeasureSet, response: Response):
    commands.measure_many(measurements)
    response.status_code = 200
    return measurements
