from loguru import logger

from pydantic.main import BaseModel
from sqlalchemy import create_engine
from sqlalchemy import MetaData

# from mangostar import module_settings as settings
from mangostar.settings import ModuleSettings
from mangostar.tables import MetaTableAdapter


settings = ModuleSettings()


def _init_tables():
    logger.info("Starting tables if they don't already exist ...")
    
    engine = create_engine(settings.postgres_connection_str)
    metadata = MetaData(bind = engine)

    adapter = MetaTableAdapter(metadata)
    metadata.create_all(engine)
    return adapter


from enum import Enum


class DBResponse(BaseModel):
    status: bool = False
    data: dict = {}
    message: str


{
    "bucket": "bakery_inventory",
    "data": {
        "id":
        "0001",
        "type":
        "donut",
        "name":
        "Cake",
        "ppu":
        0.55,
        "batters": {
            "batter": [
                {
                    "id": "1001", "type": "Regular"
                },
                {
                    "id": "1002", "type": "Chocolate"
                },
                {
                    "id": "1003", "type": "Blueberry"
                },
            ]
        },
        "topping": [
            {
                "id": "5001", "type": "None"
            }, {
                "id": "5002", "type": "Glazed"
            }, {
                "id": "5005", "type": "Sugar"
            }, {
                "id": "5007", "type": "Powdered Sugar"
            }, {
                "id": "5006", "type": "Chocolate with Sprinkles"
            }, {
                "id": "5003", "type": "Chocolate"
            }, {
                "id": "5004", "type": "Maple"
            }
        ]
    },
    "tags": {
        "store_name": "shoeberry bakery",
        "city": "los angeles",
        "state": "california",
        "id": "e662377992144ebb823628a7cb32ca6e"
    }
}
