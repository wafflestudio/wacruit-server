from datetime import timedelta
from http import HTTPStatus

from fastapi import Depends
from httpx import AsyncClient
from httpx import RequestError
from httpx._models import Response
from tenacity import retry
from tenacity import retry_if_exception_type
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

    async def submit(
        self, request: HoduSubmitRequest
    ) -> HoduSubmitResponse | HoduSubmitErrorResponse:
        try:
            return await self._submit(request)
        except (RequestError, ValueError) as exc:
            self.logger.error("Pecan API submission failed after retries: %s", exc)
            return HoduSubmitErrorResponse(
                detail=(
                    "채점 서버에 일시적인 문제가 생겼습니다. 잠시 후 다시 시도해주세요."
                )
            )

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(timedelta(seconds=1)),
        retry=retry_if_exception_type((RequestError, ValueError)),
        reraise=True,
    )
    async def _submit(
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
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            self.logger.error(
                "Pecan API ERROR for sending %s / status code: %d",
                response.url,
                response.status_code,
            )
            detail = "Unknown error"
            try:
                data = response.json()
                if isinstance(data, dict):
                    detail = (
                        data.get("InternalError") or data.get("ServiceBusy") or detail
                    )
            except ValueError:
                pass
            return HoduSubmitErrorResponse(
                detail=detail if isinstance(detail, str) else "Unknown error"
            )

        try:
            raw_data = response.json()
            if not isinstance(raw_data, dict):
                raise ValueError("Expected a JSON object from Pecan API")
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
        except (ValueError, TypeError) as exc:
            self.logger.error(
                "Pecan API RESPONSE PARSING ERROR for sending %s / status code: %d / "
                "error: %s",
                response.url,
                response.status_code,
                exc,
            )
            raise ValueError("Invalid HODU API response") from exc
