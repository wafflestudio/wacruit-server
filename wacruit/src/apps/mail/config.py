from pydantic import BaseSettings

from wacruit.src.secrets import OCISecretManager
from wacruit.src.settings import settings

_EMAIL_SECRET_KEYS = {
    "email_compartment_id": "compartment_id",
    "email_from_email": "from_email",
    "email_from_name": "from_name",
    "email_reply_to": "reply_to",
    "email_service_endpoint": "service_endpoint",
}


class MailConfig(BaseSettings):
    compartment_id: str = ""
    from_email: str = ""
    from_name: str = ""
    reply_to: str = ""
    service_endpoint: str = ""
    timeout: float = 60

    class Config(BaseSettings.Config):
        case_sensitive = False
        env_prefix = "EMAIL_"
        env_file = settings.env_files

    def __init__(self):
        super().__init__()
        secret_manager = OCISecretManager()
        if secret_manager.is_available():
            self._load_from_vault(secret_manager)

    def _load_from_vault(self, secret_manager: OCISecretManager) -> None:
        for secret_key, attr_name in _EMAIL_SECRET_KEYS.items():
            try:
                value = secret_manager.get_secret(secret_key)
            except KeyError:
                continue
            setattr(self, attr_name, value)


mail_config = MailConfig()
