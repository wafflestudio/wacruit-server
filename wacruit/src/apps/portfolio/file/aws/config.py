from pydantic import BaseSettings
from pydantic import Field

from wacruit.src.secrets import AWSSecretManager
from wacruit.src.settings import settings


class S3PortfolioConfig(BaseSettings):
    bucket_name: str = ""

    class Config:
        case_sensitive = False
        env_prefix = "S3_PORTFOLIO_"

        env_file = settings.env_files

    def __init__(self):
        super().__init__()
        aws_secrets = AWSSecretManager()
        if aws_secrets.is_available():
            self.bucket_name = aws_secrets.get_secret("portfolio_bucket_name")

    @property
    def bucket_region(self) -> str:
        return "ap-northeast-2"


s3_config = S3PortfolioConfig()
