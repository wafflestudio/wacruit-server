from typing import AsyncIterable, Callable

from dotenv import get_key
from httpx import AsyncClient

from wacruit.src.settings import settings


# pylint: disable=cell-var-from-loop
def get_api_client(env_name: str) -> Callable[[], AsyncIterable[AsyncClient]]:
    for env_file in settings.env_files:
        if base_url := get_key(env_file, env_name + "_URL"):

            async def _get_api_client() -> AsyncIterable[AsyncClient]:
                async with AsyncClient(base_url=base_url) as client:
                    yield client

            return _get_api_client

    raise ValueError("No such key in the environment files")


# pylint: enable=cell-var-from-loop
