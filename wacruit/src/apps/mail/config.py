from pydantic import BaseSettings

from wacruit.src.secrets import OCISecretManager
from wacruit.src.settings import settings

_MAIL_SECRET_KEYS = {
    "smtp_host": "host",
    "smtp_port": "port",
    "smtp_username": "username",
    "smtp_password": "password",
    "smtp_from_email": "from_email",
}


class MailConfig(BaseSettings):
    host: str = ""
    port: int = 587
    username: str = ""
    password: str = ""
    from_email: str = ""
    use_tls: bool = True

    class Config(BaseSettings.Config):
        case_sensitive = False
        env_prefix = "SMTP_"
        env_file = settings.env_files

    def __init__(self):
        super().__init__()
        secret_manager = OCISecretManager()
        if secret_manager.is_available():
            self._load_from_vault(secret_manager)

    def _load_from_vault(self, secret_manager: OCISecretManager) -> None:
        for secret_key, attr_name in _MAIL_SECRET_KEYS.items():
            value: str | int = secret_manager.get_secret(secret_key)
            if attr_name == "port":
                value = int(value)
            setattr(self, attr_name, value)


mail_config = MailConfig()
