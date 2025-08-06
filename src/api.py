from collections.abc import Callable
from os import getenv
from typing import TypeVar
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv
from pydantic import BaseModel

from src import input_models, output_models

InputModel = TypeVar("InputModel", bound=BaseModel)
OutputModel = TypeVar("OutputModel", bound=BaseModel)

load_dotenv()


class API:
    def __init__(
        self,
        base_url: str = "https://api-football-v1.p.rapidapi.com/v3/",
        api_key: str = getenv("X-RAPIDAPI-KEY"),
    ):
        self.base_url = base_url
        self.headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        }

    def _endpoint_url(self, endpoint: str):
        return urljoin(self.base_url, endpoint)

    @staticmethod
    def _validate_inputs(data: dict, input_model: type[InputModel]) -> InputModel:
        return input_model.model_validate(data)

    def _call_endpoint(self, name: str, request_method: Callable, **kwargs) -> dict:
        url = self._endpoint_url(name)
        resp = request_method(url, headers=self.headers, **kwargs)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise ValueError(f"Received invalid response: {resp.json()}")

    def _process_request(
        self,
        data: dict | type[InputModel],
        endpoint_name: str,
        request_method: Callable,
        input_model: type[InputModel],
        output_model: type[OutputModel],
        **kwargs,
    ) -> OutputModel:
        if isinstance(data, dict):
            data = self._validate_inputs(data, input_model)

        return output_model.model_validate(
            self._call_endpoint(
                endpoint_name,
                request_method=request_method,
                params=data.model_dump(exclude_unset=True),
                **kwargs,
            )
        )

    def teams(
        self, data: dict | input_models.TeamsInput
    ) -> output_models.TeamsResponse:
        return self._process_request(
            data=data,
            endpoint_name="teams",
            request_method=requests.get,
            input_model=input_models.TeamsInput,
            output_model=output_models.TeamsResponse,
        )
    
    def fixtures(
        self, data: dict | input_models.FixturesInput
    ) -> output_models.FixturesResponse:
        return self._process_request(
            data=data,
            endpoint_name="fixtures",
            request_method=requests.get,
            input_model=input_models.FixturesInput,
            output_model=output_models.FixturesResponse,
        )
