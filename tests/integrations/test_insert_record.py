import uuid
from datetime import datetime
from random import choice
from typing import Any, Dict, List, Union
from unittest.mock import MagicMock
from unittest.mock import patch

from inflection import tableize
from loguru import logger

import httpx
import hypothesis
import orjson
import pytest
from faker import Faker
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from newsapi import NewsApiClient
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import validate_arguments

from bodhi_server import commands as commandss


# from stringcase import snakecase


# class Candle(BaseModel):
#     _open: Field(..., alias="open")
#     high: float
#     low: float
#     close: float
#     volume: float
#     timestamp: datetime


# class Candles(BaseModel):
#     candles: List[Candle] = []

#     def random_pick(self) -> Candle:
#         return choice(self.candles)


# @pytest.fixture(scope="session")
# def binance_market():
#     binance = ccxt.binance()
#     markets = binance.load_markets()
#     return binance


# @pytest.fixture(scope="session")
# def news_api_sources():
#     newsapi = NewsApiClient(api_key="a3be2c2403684050898b62be104f2a40")
#     sources_response: dict = newsapi.get_sources()
#     return SourcesSet(**sources_response)


# @pytest.fixture(scope="session")
# def crypto_dataset(binance_market):
#     coin = choice(["ETH", "BTC", "ADA"])
#     pair = f"{coin}/USDT"
#     ohlcv = binance_market.fetch_ohlcv(pair, "1d")
#     candles = [
#         Candle(
#             timestamp=candle[0],
#             open=candle[1],
#             high=candle[2],
#             low=candle[3],
#             close=candle[4],
#             volume=candle[-1],
#         )
#         for candle in ohlcv
#     ]
#     return Candles(candles=candles)


# @pytest.fixture(scope="session")
# def base_client():
#     return httpx.Client(base_url="http://127.0.0.1:8000")


# def dump_json(record: dict) -> str:
#     return orjson.dumps(record).decode()


# @validate_arguments
# def create_insert_record(*, data: dict, entity: str, event_at: datetime, tags: dict):
#     return dump_json(
#         {"data": data, "bucket": entity, "event_at": event_at, "tags": tags}
#     )


# @pytest.mark.skip
# def test_create_mod_remote(crypto_dataset: Candles, base_client: httpx.Client):
#     _candle = crypto_dataset.random_pick()

#     with base_client as client:
#         resp = client.post(
#             "/record/insert",
#             content=create_insert_record(
#                 data=_candle,
#                 entity="super_candle",
#                 event_at=_candle.timestamp,
#                 tags={"hello": "world"},
#             ),
#         )

#         assert resp.status_code == httpx.codes.OK


# def test_create_candle_local(crypto_dataset: Candles):
#     _candle = crypto_dataset.random_pick()
#     comms.insert_dict(
#         bucket="super_candle",
#         tags={"hello": "world"},
#         event_at=_candle.timestamp,
#         data=_candle.dict(exclude={"timestamp"}),
#     )
#     comms.insert_dict(
#         bucket="super_candle",
#         tags={"hello": "world"},
#         event_at=_candle.timestamp,
#         data=_candle.dict(exclude={"timestamp"}),
#     )


fake = Faker()


class Source(BaseModel):
    bucket: str = Field(
        default_factory=lambda: tableize(f"{fake.first_name()}_{uuid.uuid4().hex}")
    )
    tags: dict = Field(default_factory=lambda: fake.pydict())
    data: dict = Field(default_factory=lambda: fake.profile())
    event_at: datetime = datetime.now()


# class SourcesSet(BaseModel):
#     status: str
#     sources: List[Source] = []

#     def random_pick(self) -> Source:
#         return choice(self.sources)


# # from pprint import pprint
# from string import printable

# # # st.register_type_strategy(HttpUrl, fake.image_url())
# from hypothesis.strategies import *


# dictionaries()

# json_strategy = recursive(
#     none() | booleans() | floats() | text(printable),
#     lambda children: lists(children, min_size=1)
#     | dictionaries(text(printable), children, min_size=1),
# ).filter(lambda x: x is not None)


# # @patch("bodhi_server.logic.maestro.NameMaestro.create_view", autospec=True)
# @settings(deadline=500)
@given(st.builds(Source))
def test_insert_duplicate_schema(skybringer: Source):

    # saving_data = skybringer.dict(exclude={"tags", "bucket", "event_at"})
    # logger.error(skybringer.bucket)
    # logger.success(skybringer.dict())
    commandss.insert_dict(
        bucket=skybringer.bucket,
        tags=skybringer.tags,
        data=skybringer.data,
        event_at=skybringer.event_at,
    )

    # true_view.assert_called()
