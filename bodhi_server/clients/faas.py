import os
from functools import cached_property
from typing import Iterable, Optional, Tuple

from loguru import logger

import httpx
import orjson
from httpx import Response
from pydantic import BaseModel
from pydantic import BaseSettings
from pydantic import Field
from pydantic.env_settings import SettingsSourceCallable

# NOTE:


class FaasSettings(BaseSettings):
    port: str = Field(default = "8080", env = "GATEWAY_PORT")
    host: str = Field(default = "localhost", env = "GATEWAY_HOST")
    protocol: str = Field(default = "http", env = "GATEWAY_PROTO")

    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return env_settings, init_settings, file_secret_settings

    @property
    def gateway(self) -> str:
        logger.warning(os.environ.get("GATEWAY_PORT", 8080))
        logger.warning(os.environ.get("GATEWAY_HOST", "localhost"))
        return f"{self.protocol}://{self.host}:{self.port}"


class ClientParams(BaseModel):
    name: Optional[str] = None
    stream: Optional[bool] = False
    aio: Optional[bool] = False
    forget: Optional[bool] = False

    class Config:
        extra = "ignore"

    def encoded_dict(self) -> dict:
        resp = self.dict(exclude_none = True)
        return {k: str(v).encode() for k, v in resp.items()}


class FaaSClient:
    """
        I have the basic functions out of the way. What I want to do is easily craft api calls. 
        Only problem is that I don't know what kind of OOP magic is out there.
        Maybe I could look into tensorflow and pytorch's library structure. Also, with httpx, I think the guy linked async loop detection. 
        If async loop doesn't exactly work or exist I can detect if the parent is getting called with an await function or something.

        It might be really poor design though. But what the fuck do I know. I can try it, and see if it would be a dope design decision for the main lib?

        ```python
            faas_cli = FaaSClient()
            # We could set a function parameters here.
            faas_cli(name=fn_name, stream=True, aio=True)
            
            
            # Dumping input into the function via json.
            dict_data: dict = {}
            faas_cli(dict_data)
            
            
            async with faas_cli:

                # Dumping input into the json.
                dict_data: dict = {}
                faas_cli(dict_data)


                # We would detect if this is something to stream into the function and split it
                dict_set_data = [{}]
                faas_cli(dict_set_data)
                
        ```
    """

    # TODO: After basics are done it would be adventagous to split this into other variables in this class
    # NOTE: Might be better as a cached property
    def __init__(self):
        self.settings: FaasSettings = FaasSettings()
        self.params: ClientParams = ClientParams()

    @cached_property
    def gateway(self):
        return self.settings.gateway

    @cached_property
    def client(self) -> httpx.Client:
        return httpx.Client(base_url = self.gateway)

    @cached_property
    def async_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url = self.gateway)

    def fn_str(self, fn_name: str, is_async: bool = False) -> str:
        if not is_async:
            return f"function/{fn_name}"
        return f"async-function/{fn_name}"

    def make_request(
        self,
        function_name: str,
        is_async: bool = False,
        data: dict = {}
    ) -> Response:
        """Make a request to the API .

        Args:
            function_name (str): The function's name.
            is_async (bool, optional): Determines if we're pushing the code to an async queue. Defaults to False.

        Returns:
            Response: A response from the call.
        """
        url = self.fn_str(function_name, is_async = is_async)
        return self.client.post(
            url = url, content = orjson.dumps({
                "data": data
            }).decode()
        )

    async def make_request_aio(
        self, function_name: str, is_async: bool = False
    ) -> Response:
        """Request a function with asyncio .

        Args:
            function_name (str): The function name.
            is_async (bool, optional): Determines if we're pushing the code to an async queue. Defaults to False.

        Returns:
            Response: [description]
        """
        url = self.fn_str(
            function_name,
            is_async = is_async,
        )
        return await self.async_client.post(url = url)

    async def make_request_stream(self, fn_name: str) -> Iterable[Response]:
        url = self.fn_str(fn_name)
        resp_stream = self.async_client.stream(url = f"{url}/async/stream")
        for chunck in resp_stream:
            yield chunck

    def set_args(self, **kwargs):
        # is_global means merge update
        _is_global = kwargs.get("is_global", None)

        # Setting the client parameters here.
        params = ClientParams(**kwargs)
        recent = params.dict(exclude_none = True)

        if not recent:
            return
        if _is_global and _is_global == True:

            previous = self.params.dict(exclude_none = True)
            previous.update(recent)
            self.params = ClientParams(**previous)
            return
        self.params = params

    def __call__(self, *inputs, data: dict = {}, **kwargs):
        """
            Sending in http call with input information. The name would be either set with the kwargs or prior to that point.
        """
        not_input = bool(inputs)

        if bool(kwargs):
            if not_input:
                if "is_global" not in kwargs:
                    kwargs['is_global'] = True
            self.set_args(**kwargs)

        if not_input:
            if not data:
                logger.debug("We're likely just setting settings here.")
                return Response(
                    404, json = {"message": "You didn't add any information."}
                )
            return self.make_request(
                self.params.name, is_async = self.params.forget, data = data
            )

        return self.make_request(
            self.params.name, is_async = self.params.forget, data = inputs
        )
