from pydantic import BaseSettings

from wacruit.src.secrets import AWSSecretManager
from wacruit.src.settings import settings


class JudgeAPIConfig(BaseSettings):
    url: str = ""

    class Config:
        case_sensitive = False
        env_prefix = "JUDGE_"
        env_file = settings.env_files

    def __init__(self) -> None:
        super().__init__()
        aws_secrets = AWSSecretManager()
        if aws_secrets.is_available():
            self.url = aws_secrets.get_secret("judge_api_url")


judge_api_config = JudgeAPIConfig()
