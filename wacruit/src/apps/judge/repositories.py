from typing import Iterable

from fastapi import Depends
from httpx import AsyncClient

from . import get_judge_api_client
from .schemas import JudgeCreateSubmissionRequest
from .schemas import JudgeCreateSubmissionResponse
from .schemas import JudgeGetSubmissionResponse

DEFAULT_PARAMS = {"base64_encoded": False}
DEFAULT_FIELDS = "stdout,stderr,compile_output,message,status,time,memory"


class JudgeApiRepository:
    def __init__(self, client: AsyncClient = Depends(get_judge_api_client)):
        self.client = client

    async def create_submission(
        self, request: JudgeCreateSubmissionRequest
    ) -> JudgeCreateSubmissionResponse:
        res = await self.client.post(
            url="/submissions",
            params=DEFAULT_PARAMS,
            json=request.dict(),
            timeout=60,
        )
        res.raise_for_status()
        return JudgeCreateSubmissionResponse(**res.json())

    async def create_batch_submissions(
        self, requests: list[JudgeCreateSubmissionRequest]
    ) -> list[JudgeCreateSubmissionResponse]:
        batch_request_data = {"submissions": [request.dict() for request in requests]}
        res = await self.client.post(
            url="/submissions/batch",
            params=DEFAULT_PARAMS,
            json=batch_request_data,
            timeout=60,
        )
        res.raise_for_status()
        return [JudgeCreateSubmissionResponse(**v) for v in res.json()]

    async def get_submission(self, token: str) -> JudgeGetSubmissionResponse:
        res = await self.client.get(
            url=f"/submissions/{token}",
            params={**DEFAULT_PARAMS, "fields": ",".join(DEFAULT_FIELDS)},
            timeout=60,
        )
        res.raise_for_status()
        return JudgeGetSubmissionResponse(**res.json())

    async def get_batch_submissions(
        self, tokens: Iterable[str] | str
    ) -> list[JudgeGetSubmissionResponse]:
        if isinstance(tokens, Iterable):
            tokens = ",".join(tokens)
        res = await self.client.get(
            url="/submissions/batch",
            params={"tokens": tokens, **DEFAULT_PARAMS, "fields": DEFAULT_FIELDS},
            timeout=60,
        )
        res.raise_for_status()
        submissions = res.json()["submissions"]
        return [JudgeGetSubmissionResponse(**v) for v in submissions]
