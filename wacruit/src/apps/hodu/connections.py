from typing import AsyncGenerator

from httpx import AsyncClient

from .config import hodu_api_config


async def get_hodu_api_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        base_url=hodu_api_config.url,
        timeout=30,
        headers={"X-Hodu-Api-Key": hodu_api_config.api_key},
    ) as client:
        yield client
