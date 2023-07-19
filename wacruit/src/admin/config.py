from pydantic import BaseSettings

from wacruit.src.secrets import AWSSecretManager


class AdminConfig(BaseSettings):
    username: str = "admin"
    password: str = "admin"
    expires_in: int = 3600  # seconds

    def __init__(self) -> None:
        super().__init__()
        aws_secrets = AWSSecretManager()
        if aws_secrets.is_available():
            self.username = aws_secrets.get_secret("admin_username")
            self.password = aws_secrets.get_secret("admin_password")


admin_config = AdminConfig()
