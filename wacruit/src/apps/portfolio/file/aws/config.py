from pydantic import BaseSettings

from wacruit.src.secrets import OCISecretManager
from wacruit.src.settings import settings

_REQUIRED_OBJECT_STORAGE_SECRET_KEYS = {
    "object_storage_bucket_name": "bucket_name",
    "object_storage_region": "region",
    "object_storage_endpoint_url": "endpoint_url",
    "object_storage_access_key_id": "access_key_id",
    "object_storage_secret_access_key": "secret_access_key",
}


class StorageConfig(BaseSettings):
    bucket_name: str = ""
    region: str = "ap-northeast-2"
    endpoint_url: str | None = None
    access_key_id: str | None = None
    secret_access_key: str | None = None
    addressing_style: str = "path"

    class Config(BaseSettings.Config):
        case_sensitive = False
        env_prefix = "OBJECT_STORAGE_"
        env_file = settings.env_files

    def __init__(self):
        super().__init__()
        secret_manager = OCISecretManager()
        if secret_manager.is_available():
            self._load_from_vault(secret_manager)

    def _load_from_vault(self, secret_manager: OCISecretManager) -> None:
        missing_keys: list[str] = []
        for secret_key, attr_name in _REQUIRED_OBJECT_STORAGE_SECRET_KEYS.items():
            try:
                value = secret_manager.get_secret(secret_key)
            except KeyError:
                missing_keys.append(secret_key)
                continue

            if not value:
                missing_keys.append(secret_key)
                continue

            setattr(self, attr_name, value)

        if missing_keys:
            raise ValueError(
                "Missing required object storage secret keys in OCI Vault: "
                + ", ".join(missing_keys)
            )


storage_config = StorageConfig()
