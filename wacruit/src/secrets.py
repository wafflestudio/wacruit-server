import json

from aws_secretsmanager_caching import SecretCache
from aws_secretsmanager_caching import SecretCacheConfig
import botocore
import botocore.session

from wacruit.src.settings import settings


class AWSSecretManager:
    def __init__(self) -> None:
        client = botocore.session.get_session().create_client(
            "secretsmanager", region_name="ap-northeast-2"
        )
        cache_config = SecretCacheConfig()
        self.cache = SecretCache(config=cache_config, client=client)
        self.secret_name = f"{settings.env}/wacruit-server"

    def is_available(self) -> bool:
        if settings.env in ["local", "test"]:
            return False
        try:
            self.cache.get_secret_string(secret_id=self.secret_name)
            return True
        except BaseException:
            return False

    def get_secret(self, key: str) -> str:
        assert self.is_available(), "Secret Manager is not available"
        secret_data = json.loads(
            self.cache.get_secret_string(secret_id=self.secret_name)
        )
        return secret_data[key]
