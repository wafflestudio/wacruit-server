import os
from typing import Literal, cast
from urllib.parse import urlparse

from botocore.client import BaseClient
import pytest

from wacruit.src.apps.portfolio.file.aws.config import StorageConfig
from wacruit.src.apps.portfolio.file.aws.s3.client import S3Client
from wacruit.src.apps.portfolio.file.aws.s3.method import S3PresignedUrlMethod
from wacruit.src.apps.portfolio.file.aws.s3.utils import (
    generate_presigned_post_url,
    generate_presigned_url,
)
from wacruit.src.secrets import OCISecretManager
from wacruit.src.settings import settings
from wacruit.src.utils.singleton import SingletonMeta

_TargetEnv = Literal["dev", "prod", "local"]
_RUN_LIVE_TEST_REASON = (
    "Set RUN_ORACLE_SECRET_TEST=1 to run live Oracle presigned URL contract checks."
)


def _reset_singletons() -> None:
    for singleton_cls in (OCISecretManager, S3Client):
        SingletonMeta._instances.pop(singleton_cls, None)


def _target_env() -> _TargetEnv:
    if os.getenv("ORACLE_SECRET_SOURCE", "env") == "vault":
        target_env = os.getenv("ORACLE_SECRET_TEST_ENV", "dev")
        assert target_env in {"dev", "prod"}
        return cast(_TargetEnv, target_env)
    return "local"


def _build_storage_context() -> tuple[StorageConfig, BaseClient]:
    settings.env = cast(Literal["dev", "prod", "local", "test"], _target_env())
    _reset_singletons()
    storage_config = StorageConfig()
    s3_client = S3Client().client
    return storage_config, s3_client


def _assert_post_contract(storage_config: StorageConfig, object_key: str) -> None:
    _, s3_client = _build_storage_context()
    post_url, fields = generate_presigned_post_url(
        s3_client=s3_client,
        s3_bucket=storage_config.bucket_name,
        s3_object=object_key,
        expires_in=600,
    )

    parsed = urlparse(post_url)
    endpoint = urlparse(storage_config.endpoint_url)

    assert parsed.scheme == endpoint.scheme
    assert parsed.netloc == endpoint.netloc
    assert parsed.path == f"/{storage_config.bucket_name}"
    assert fields["key"] == object_key
    assert fields["x-amz-algorithm"] == "AWS4-HMAC-SHA256"
    assert fields["x-amz-credential"].endswith(
        f"/{storage_config.region}/s3/aws4_request"
    )
    assert "x-amz-date" in fields
    assert "policy" in fields
    assert "x-amz-signature" in fields


def _assert_get_contract(storage_config: StorageConfig, object_key: str) -> None:
    _, s3_client = _build_storage_context()
    get_url = generate_presigned_url(
        s3_client=s3_client,
        client_method=S3PresignedUrlMethod.GET,
        method_parameters={
            "Bucket": storage_config.bucket_name,
            "Key": object_key,
        },
        expires_in=600,
    )
    url, _ = get_url.split("?")

    parsed = urlparse(url)
    endpoint = urlparse(storage_config.endpoint_url)

    assert parsed.scheme == endpoint.scheme
    assert parsed.netloc == endpoint.netloc
    assert parsed.path == f"/{storage_config.bucket_name}/{object_key}"


@pytest.mark.skipif(
    os.getenv("RUN_ORACLE_SECRET_TEST") != "1",
    reason=_RUN_LIVE_TEST_REASON,
)
def test_oracle_presigned_contract_for_portfolio_object_key():
    storage_config, _ = _build_storage_context()
    assert storage_config.endpoint_url

    object_key = "123/test.pdf"
    _assert_post_contract(storage_config, object_key)
    _assert_get_contract(storage_config, object_key)


@pytest.mark.skipif(
    os.getenv("RUN_ORACLE_SECRET_TEST") != "1",
    reason=_RUN_LIVE_TEST_REASON,
)
def test_oracle_presigned_contract_for_project_object_key():
    storage_config, _ = _build_storage_context()
    assert storage_config.endpoint_url

    object_key = "PROJECT/42/image.png"
    _assert_post_contract(storage_config, object_key)
    _assert_get_contract(storage_config, object_key)
