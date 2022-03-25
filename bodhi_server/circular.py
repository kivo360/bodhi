from loguru import logger

from pydantic.main import BaseModel
from sqlalchemy import create_engine
from sqlalchemy import MetaData

# from bodhi_server import module_settings as settings
from bodhi_server.settings import ModuleSettings
from bodhi_server.tables import MetaTableAdapter


settings = ModuleSettings()
TABLE_ADAPTER: MetaTableAdapter = None


def _init_tables():
    logger.info("Starting tables if they don't already exist ...")

    engine = create_engine(settings.postgres_connection_str)
    metadata = MetaData(bind=engine)

    adapter = MetaTableAdapter(metadata)
    metadata.create_all(engine)
    return adapter


def init():
    global TABLE_ADAPTER
    adapter = _init_tables()
    if not TABLE_ADAPTER:
        TABLE_ADAPTER = adapter
    return adapter


class DBResponse(BaseModel):
    status: bool = False
    data: dict = {}
    message: str


def main():
    example_data = {
        "bucket": "bakery_inventory",
        "data": {
            "id": "0001",
            "type": "donut",
            "name": "Cake",
            "ppu": 0.55,
            "batters": {
                "batter": [
                    {"id": "1001", "type": "Regular"},
                    {"id": "1002", "type": "Chocolate"},
                    {"id": "1003", "type": "Blueberry"},
                ]
            },
            "topping": [
                {"id": "5001", "type": "None"},
                {"id": "5002", "type": "Glazed"},
                {"id": "5005", "type": "Sugar"},
                {"id": "5007", "type": "Powdered Sugar"},
                {"id": "5006", "type": "Chocolate with Sprinkles"},
                {"id": "5003", "type": "Chocolate"},
                {"id": "5004", "type": "Maple"},
            ],
        },
        "tags": {
            "store_name": "shoeberry bakery",
            "city": "los angeles",
            "state": "california",
            "id": "e662377992144ebb823628a7cb32ca6e",
        },
    }


if __name__ == "__main__":
    main()
