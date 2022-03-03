from typing import Optional, Union

from loguru import logger

from pydantic import BaseModel


class FlexibleModel(BaseModel):
    class Config:
        extra = 'allow'
        arbitrary_types_allowed = 'allow'
