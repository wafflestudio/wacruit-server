from typing import AsyncIterable

from httpx import AsyncClient

from .config import judge_api_config


async def get_judge_api_client() -> AsyncIterable[AsyncClient]:
    async with AsyncClient(base_url=judge_api_config.URL) as client:
        yield client
