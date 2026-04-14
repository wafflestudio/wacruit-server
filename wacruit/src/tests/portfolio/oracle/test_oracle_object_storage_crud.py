import os
from typing import Literal, cast
from uuid import uuid4

from botocore.client import BaseClient
from botocore.exceptions import ClientError
import httpx
import pytest

from wacruit.src.apps.portfolio.file.aws.config import StorageConfig
from wacruit.src.apps.portfolio.file.aws.s3.client import S3Client
from wacruit.src.apps.portfolio.file.aws.s3.method import S3PresignedUrlMethod
from wacruit.src.apps.portfolio.file.aws.s3.utils import (
    delete_object,
    generate_presigned_post_url,
    generate_presigned_url,
)
from wacruit.src.secrets import OCISecretManager
from wacruit.src.settings import settings
from wacruit.src.utils.singleton import SingletonMeta

_PAYLOAD = b"oracle object storage integration test"
_TargetEnv = Literal["dev", "prod", "local"]
_RUN_LIVE_TEST_REASON = (
    "Set RUN_ORACLE_SECRET_TEST=1 to run live Oracle Object Storage CRUD checks."
)
_HTTP_STATUS_NO_CONTENT = 204
_HTTP_STATUS_OK = 200


def _reset_singletons() -> None:
    for singleton_cls in (OCISecretManager, S3Client):
        SingletonMeta._instances.pop(singleton_cls, None)


def _secret_source() -> Literal["env", "vault"]:
    source = os.getenv("ORACLE_SECRET_SOURCE", "env")
    assert source in {"env", "vault"}
    return cast(Literal["env", "vault"], source)


def _target_env() -> _TargetEnv:
    if _secret_source() == "vault":
        target_env = os.getenv("ORACLE_SECRET_TEST_ENV", "dev")
        assert target_env in {"dev", "prod"}
        return cast(_TargetEnv, target_env)
    return "local"


def _build_storage_context() -> tuple[StorageConfig, BaseClient]:
    settings.env = cast(Literal["dev", "prod", "local", "test"], _target_env())
    _reset_singletons()
    storage_config = StorageConfig()
    s3_client = S3Client().client

    assert storage_config.bucket_name
    assert storage_config.region
    assert storage_config.endpoint_url
    assert storage_config.access_key_id
    assert storage_config.secret_access_key

    return storage_config, s3_client


@pytest.mark.skipif(
    os.getenv("RUN_ORACLE_SECRET_TEST") != "1",
    reason=_RUN_LIVE_TEST_REASON,
)
def test_oracle_object_storage_upload_download_delete_roundtrip():
    storage_config, s3_client = _build_storage_context()
    object_key = f"codex-oracle-smoke/{uuid4()}.txt"

    presigned_post_url, fields = generate_presigned_post_url(
        s3_client=s3_client,
        s3_bucket=storage_config.bucket_name,
        s3_object=object_key,
        expires_in=600,
    )

    upload_response = httpx.post(
        presigned_post_url,
        data=fields,
        files={"file": ("smoke.txt", _PAYLOAD, "text/plain")},
        timeout=30.0,
    )
    assert upload_response.status_code == _HTTP_STATUS_NO_CONTENT, upload_response.text

    presigned_get_url = generate_presigned_url(
        s3_client=s3_client,
        client_method=S3PresignedUrlMethod.GET,
        method_parameters={
            "Bucket": storage_config.bucket_name,
            "Key": object_key,
        },
        expires_in=600,
    )
    download_response = httpx.get(presigned_get_url, timeout=30.0)
    assert download_response.status_code == _HTTP_STATUS_OK
    assert download_response.content == _PAYLOAD

    delete_object(
        s3_client=s3_client,
        s3_bucket=storage_config.bucket_name,
        s3_object=object_key,
    )

    with pytest.raises(ClientError):
        s3_client.head_object(
            Bucket=storage_config.bucket_name,
            Key=object_key,
        )
