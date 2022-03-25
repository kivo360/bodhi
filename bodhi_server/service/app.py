from datetime import datetime
from typing import Any, Dict, Optional

from devtools import debug
from inflection import tableize
from loguru import logger

from addict import Addict as DDict
from fastapi import FastAPI, Response
from pydantic import BaseModel
from pydantic import root_validator
from bodhi_server import commands, models
from bodhi_server import circular as circle
from bodhi_server import settings
from bodhi_server.circular import DBResponse
from bodhi_server.settings import ModuleSettings
from bodhi_server.utils import InsertParameters
from bodhi_server.service.routers import chat

settings_root = ModuleSettings()

app = FastAPI()
app.include_router(chat.router, prefix="/chat", tags=["websocket", "broadcast"])


@app.on_event("startup")
async def start_databases():
    # logger.info(settings.postgres_connection_str)
    table = circle.init()
    logger.error(settings_root.postgres_connection_str)
    logger.info(table)


@app.post("/insert", response_model=DBResponse)
def insert_item(item: InsertParameters):
    return commands.ingest_data(**item.dict())


@app.post("/measure")
def record_measurement(measurements: models.MeasureSet, response: Response):
    commands.measure_many(measurements)
    response.status_code = 200
    return measurements
