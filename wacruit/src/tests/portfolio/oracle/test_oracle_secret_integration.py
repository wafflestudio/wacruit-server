import os
from typing import Literal, cast

import pytest

from wacruit.src.apps.portfolio.file.aws.config import StorageConfig
from wacruit.src.apps.portfolio.file.aws.s3.client import S3Client
from wacruit.src.secrets import OCISecretManager
from wacruit.src.settings import settings
from wacruit.src.utils.singleton import SingletonMeta

_REQUIRED_STORAGE_SECRET_KEYS = [
    "object_storage_bucket_name",
    "object_storage_region",
    "object_storage_endpoint_url",
    "object_storage_access_key_id",
    "object_storage_secret_access_key",
]
_TargetEnv = Literal["dev", "prod", "local"]
_RUN_LIVE_TEST_REASON = (
    "Set RUN_ORACLE_SECRET_TEST=1 to run live Oracle Secret/Object Storage checks."
)
_HTTP_STATUS_OK = 200


def _reset_singletons() -> None:
    for singleton_cls in (OCISecretManager, S3Client):
        SingletonMeta._instances.pop(singleton_cls, None)


def _build_storage_config(target_env: _TargetEnv) -> StorageConfig:
    settings.env = cast(Literal["dev", "prod", "local", "test"], target_env)
    _reset_singletons()
    return StorageConfig()


def _secret_source() -> Literal["env", "vault"]:
    source = os.getenv("ORACLE_SECRET_SOURCE", "env")
    assert source in {"env", "vault"}
    return cast(Literal["env", "vault"], source)


def _target_env() -> _TargetEnv:
    source = _secret_source()
    if source == "vault":
        target_env = os.getenv("ORACLE_SECRET_TEST_ENV", "dev")
        assert target_env in {"dev", "prod"}
        return cast(_TargetEnv, target_env)
    return "local"


@pytest.mark.skipif(
    os.getenv("RUN_ORACLE_SECRET_TEST") != "1",
    reason=_RUN_LIVE_TEST_REASON,
)
def test_storage_configuration_is_available():
    source = _secret_source()
    target_env = _target_env()

    if source == "vault":
        assert target_env in {"dev", "prod"}

        settings.env = cast(Literal["dev", "prod", "local", "test"], target_env)
        _reset_singletons()

        secret_manager = OCISecretManager()
        assert secret_manager.is_available() is True

        for key in _REQUIRED_STORAGE_SECRET_KEYS:
            value = secret_manager.get_secret(key)
            assert value, f"Vault secret key '{key}' is missing or empty."
        return

    assert source == "env"
    storage_config = _build_storage_config(target_env)
    assert storage_config.bucket_name
    assert storage_config.region
    assert storage_config.endpoint_url
    assert storage_config.access_key_id
    assert storage_config.secret_access_key


@pytest.mark.skipif(
    os.getenv("RUN_ORACLE_SECRET_TEST") != "1",
    reason=_RUN_LIVE_TEST_REASON,
)
def test_oracle_secret_backed_storage_client_can_connect_to_bucket():
    target_env = _target_env()
    storage_config = _build_storage_config(target_env)

    assert storage_config.bucket_name
    assert storage_config.region
    assert storage_config.endpoint_url
    assert storage_config.access_key_id
    assert storage_config.secret_access_key

    s3_client = S3Client().client

    # Bucket metadata lookup verifies that the Vault-backed credentials can
    # authenticate against Oracle Object Storage for the configured bucket.
    s3_client.head_bucket(Bucket=storage_config.bucket_name)

    response = s3_client.list_objects_v2(
        Bucket=storage_config.bucket_name,
        MaxKeys=1,
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == _HTTP_STATUS_OK
