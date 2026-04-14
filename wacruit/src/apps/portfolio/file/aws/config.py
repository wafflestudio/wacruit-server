from pydantic import BaseSettings

from wacruit.src.secrets import OCISecretManager
from wacruit.src.settings import settings


class StorageConfig(BaseSettings):
    bucket_name: str = ""
    region: str = "ap-northeast-2"
    endpoint_url: str | None = None
    access_key_id: str | None = None
    secret_access_key: str | None = None
    addressing_style: str = "path"

    class Config:
        case_sensitive = False
        env_prefix = "OBJECT_STORAGE_"
        env_file = settings.env_files

    def __init__(self):
        super().__init__()
        secret_manager = OCISecretManager()
        if secret_manager.is_available():
            self.bucket_name = secret_manager.get_secret("object_storage_bucket_name")
            self.region = secret_manager.get_secret("object_storage_region")
            self.endpoint_url = secret_manager.get_secret("object_storage_endpoint_url")
            self.access_key_id = secret_manager.get_secret(
                "object_storage_access_key_id"
            )
            self.secret_access_key = secret_manager.get_secret(
                "object_storage_secret_access_key"
            )


storage_config = StorageConfig()
