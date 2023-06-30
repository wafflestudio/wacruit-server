from pydantic import BaseSettings

from wacruit.src.secrets import AWSSecretManager
from wacruit.src.settings import settings


class DBConfig(BaseSettings):
    username: str = ""
    password: str = ""
    host: str = ""
    port: int = 0
    name: str = ""

    class Config:
        case_sensitive = False
        env_prefix = "DB_"

        env_file = settings.env_files

    @property
    def url(self) -> str:
        aws_secrets = AWSSecretManager()
        if aws_secrets.is_available():
            self.username = aws_secrets.get_secret("server_db_username")
            self.password = aws_secrets.get_secret("server_db_password")
            self.host = aws_secrets.get_secret("server_db_host")
            self.port = int(aws_secrets.get_secret("server_db_port"))
            self.name = aws_secrets.get_secret("server_db_name")

        return (
            f"mysql+mysqldb://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


db_config = DBConfig()
