from pydantic import BaseSettings

from wacruit.src.settings import settings


class JudgeAPIConfig(BaseSettings):
    url: str = ""

    class Config:
        case_sensitive = False
        env_prefix = "JUDGE_"
        env_file = settings.env_files


judge_api_config = JudgeAPIConfig()
