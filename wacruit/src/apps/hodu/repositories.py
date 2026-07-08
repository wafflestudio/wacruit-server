from datetime import timedelta
from typing import Iterable

from fastapi import Depends
from httpx import AsyncClient
from httpx._models import Response
from pydantic.error_wrappers import ValidationError
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from wacruit.src.apps.hodu.schemas import HoduSubmitError
from wacruit.src.apps.hodu.schemas import HoduSubmitErrorResponse
from wacruit.src.apps.hodu.schemas import HoduSubmitRequest
from wacruit.src.apps.hodu.schemas import HoduSubmitResponse
from wacruit.src.utils.mixins import LoggingMixin

from .connections import get_hodu_api_client


class HoduApiRepository(LoggingMixin):
    def __init__(self, client: AsyncClient = Depends(get_hodu_api_client)):
        self.client = client

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(timedelta(seconds=1)))
    async def submit(
        self, request: HoduSubmitRequest
    ) -> HoduSubmitResponse | HoduSubmitErrorResponse:
        res = await self.client.post(
            url="/api/v1/submit",
            json=request.dict(),
            timeout=60,
        )
        return self._parse_response(res)

    def _parse_response(
        self, response: Response
    ) -> HoduSubmitResponse | HoduSubmitErrorResponse:
        try:
            if response.status_code >= 400:
                self.logger.error(
                    "HODU API ERROR for sending %s / status code: %d / response: %s",
                    response.url,
                    response.status_code,
                    response.json(),
                )
                return HoduSubmitErrorResponse(**response.json())
            return HoduSubmitResponse(**response.json())
        except ValidationError as e:
            self.logger.error(
                "HODU API RESPONSE PARSING ERROR for sending %s / status code: %d / "
                "response: %s / error: %s",
                response.url,
                response.status_code,
                response.json(),
                e,
            )
            raise e
