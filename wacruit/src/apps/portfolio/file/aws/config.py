from pydantic import BaseSettings

from wacruit.src.settings import settings


class S3PortfolioConfig(BaseSettings):
    bucket_name: str = ""
    bucket_region: str = ""

    class Config:
        case_sensitive = False
        env_prefix = "S3_PORTFOLIO_"

        env_file = settings.env_files


s3_config = S3PortfolioConfig()
