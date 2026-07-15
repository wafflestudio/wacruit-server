from datetime import timedelta
from http import HTTPStatus

from fastapi import Depends
from httpx import AsyncClient
from httpx._models import Response
from pydantic.error_wrappers import ValidationError
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

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
        payload = {
            "code": request.code,
            "language": request.language.value,
            "stdin": request.stdin,
            "desired_stdout": request.expected_stdout,
            "time_limit": request.time_limit,
            "memory_limit": float(request.memory_limit),
        }
        res = await self.client.post(
            url="/v1/judge/judge-single",
            json=payload,
            timeout=60,
        )
        return self._parse_response(res)

    def _parse_response(
        self, response: Response
    ) -> HoduSubmitResponse | HoduSubmitErrorResponse:
        try:
            if response.status_code >= HTTPStatus.BAD_REQUEST:
                self.logger.error(
                    "HODU API ERROR for sending %s / status code: %d / response: %s",
                    response.url,
                    response.status_code,
                    response.json(),
                )
                data = response.json()
                detail = (
                    data.get("InternalError")
                    or data.get("ServiceBusy")
                    or "Unknown error"
                )
                return HoduSubmitErrorResponse(detail=detail)

            raw_data = response.json()
            mapped_data = {
                "status": raw_data.get("status"),
                "fields": {
                    "time": raw_data.get("time"),
                    "memory": int(raw_data["memory"])
                    if raw_data.get("memory") is not None
                    else None,
                    "stdout": raw_data.get("stdout"),
                    "stderr": raw_data.get("stderr"),
                },
            }
            return HoduSubmitResponse(**mapped_data)
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
