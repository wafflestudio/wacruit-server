from typing import AsyncGenerator

from httpx import AsyncClient

from .config import judge_api_config


async def get_judge_api_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        base_url=judge_api_config.url,
        headers={"X-RapidAPI-Key": judge_api_config.api_key},
    ) as client:
        yield client
