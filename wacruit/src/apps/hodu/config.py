from fastapi.security import api_key
from pydantic import BaseSettings

from wacruit.src.secrets import AWSSecretManager
from wacruit.src.settings import settings


class HoduAPIConfig(BaseSettings):
    url: str = ""
    api_key: str = ""

    class Config:
        case_sensitive = False
        env_prefix = "HODU_"
        env_file = settings.env_files

    def __init__(self) -> None:
        super().__init__()
        aws_secrets = AWSSecretManager()
        if aws_secrets.is_available():
            self.url = aws_secrets.get_secret("hodu_api_url")
            self.api_key = aws_secrets.get_secret("hodu_api_key")


hodu_api_config = HoduAPIConfig()
