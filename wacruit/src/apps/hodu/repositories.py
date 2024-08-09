from typing import Iterable

from fastapi import Depends
from httpx import AsyncClient

from wacruit.src.apps.hodu.schemas import HoduSubmitErrorResponse
from wacruit.src.apps.hodu.schemas import HoduSubmitRequest
from wacruit.src.apps.hodu.schemas import HoduSubmitResponse

from .connections import get_hodu_api_client


class HoduApiRepository:
    def __init__(self, client: AsyncClient = Depends(get_hodu_api_client)):
        self.client = client

    async def submit(
        self, request: HoduSubmitRequest
    ) -> HoduSubmitResponse | HoduSubmitErrorResponse:
        res = await self.client.post(
            url="/api/v1/submit",
            json=request.dict(),
            timeout=60,
        )
        if res.status_code >= 400:
            print(f"ERROR for sending {res.url} / status code: {res.status_code}.")
            print(f"Details: {res.json()}")
            return HoduSubmitErrorResponse(**res.json())
        return HoduSubmitResponse(**res.json())
