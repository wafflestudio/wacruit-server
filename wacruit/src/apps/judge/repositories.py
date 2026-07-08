from typing import Iterable

from fastapi import Depends
from httpx import AsyncClient

from .connections import get_judge_api_client
from .schemas import JudgeCreateSubmissionRequest
from .schemas import JudgeCreateSubmissionResponse
from .schemas import JudgeGetSubmissionResponse

# DEFAULT_FIELDS = "stdout,stderr,compile_output,message,status,time,memory"
DEFAULT_FIELDS = "stdout,message,status,time,memory"


class JudgeApiRepository:
    def __init__(self, client: AsyncClient = Depends(get_judge_api_client)):
        self.client = client

    async def create_submission(
        self, request: JudgeCreateSubmissionRequest
    ) -> JudgeCreateSubmissionResponse:
        res = await self.client.post(
            url="/submissions",
            params={"base64_encoded": False},
            json=request.dict(),
            timeout=60,
        )
        if res.status_code >= 400:
            print(f"ERROR for sending {res.url} / status code: {res.status_code}.")
            print(f"Details: {res.text}")
        res.raise_for_status()
        return JudgeCreateSubmissionResponse(**res.json())

    async def create_batch_submissions(
        self, requests: list[JudgeCreateSubmissionRequest]
    ) -> list[JudgeCreateSubmissionResponse]:
        batch_request_data = {"submissions": [request.dict() for request in requests]}
        res = await self.client.post(
            url="/submissions/batch",
            params={"base64_encoded": False},
            json=batch_request_data,
            timeout=60,
        )
        if res.status_code >= 400:
            print(f"ERROR for sending {res.url} / status code: {res.status_code}.")
            print(f"Details: {res.text}")
        res.raise_for_status()
        return [JudgeCreateSubmissionResponse(**v) for v in res.json()]

    async def get_submission(self, token: str) -> JudgeGetSubmissionResponse:
        res = await self.client.get(
            url=f"/submissions/{token}",
            params={
                "base64_encoded": True,
                "fields": DEFAULT_FIELDS,
            },
            timeout=60,
        )
        if res.status_code >= 400:
            print(f"ERROR for sending {res.url} / status code: {res.status_code}.")
            print(f"Details: {res.text}")
        res.raise_for_status()
        return JudgeGetSubmissionResponse(**res.json())

    async def get_batch_submissions(
        self, tokens: Iterable[str] | str
    ) -> list[JudgeGetSubmissionResponse]:
        if isinstance(tokens, Iterable):
            tokens = ",".join(tokens)
        res = await self.client.get(
            url="/submissions/batch",
            params={
                "tokens": tokens,
                "base64_encoded": True,
                "fields": DEFAULT_FIELDS,
            },
            timeout=60,
        )
        if res.status_code >= 400:
            print(f"ERROR for sending {res.url} / status code: {res.status_code}.")
            print(f"Details: {res.text}")
        res.raise_for_status()
        submissions = res.json()["submissions"]
        return [JudgeGetSubmissionResponse(**v) for v in submissions]
