from fastapi import Depends
from httpx import AsyncClient

from . import get_judge_api_client
from .schemas import JudgeCreateSubmissionRequest
from .schemas import JudgeCreateSubmissionResponse
from .schemas import JudgeGetSubmissionResponse


class JudgeApiRepository:
    def __init__(self, client: AsyncClient = Depends(get_judge_api_client)):
        self.client = client

    async def create_submission(
        self, request: JudgeCreateSubmissionRequest
    ) -> JudgeCreateSubmissionResponse:
        res = await self.client.post(
            url="/submissions?base64_encoded=false", data=request.dict(), timeout=60
        )
        res.raise_for_status()
        return JudgeCreateSubmissionResponse(**res.json())

    async def list_submission(self, fields: list[str]) -> JudgeGetSubmissionResponse:
        res = await self.client.get(
            url="/submissions?base64_encoded=false",
            params={"fields": ",".join(fields)},
            timeout=60,
        )
        res.raise_for_status()
        return JudgeGetSubmissionResponse(**res.json())

    async def get_submission(
        self, token: str, fields: list[str] | None = None
    ) -> JudgeGetSubmissionResponse:
        res = await self.client.get(
            url=f"/submissions/{token}?base64_encoded=false",
            params=fields and {"fields": ",".join(fields)},  # type: ignore
            timeout=60,
        )
        res.raise_for_status()
        return JudgeGetSubmissionResponse(**res.json())
