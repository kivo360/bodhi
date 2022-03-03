import time
from typing import Callable

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.routing import APIRoute




router = APIRouter(prefix="/events", tags=['events'] )


@router.get("/")
async def not_timed():
    return {"message": "Not timed"}


@router.post("/capture")
async def timed():
    return {"message": "It's the time of my life"}


