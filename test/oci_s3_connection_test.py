from __future__ import annotations

import os
import sys

import boto3
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required env: {name}")
    return value


def _make_s3_client() -> BaseClient:
    load_dotenv(".env.test")
    access_key = _required_env("OCI_ACCESS_KEY_ID")
    secret_key = _required_env("OCI_SECRET_ACCESS_KEY")
    endpoint_url = _required_env("OCI_S3_COMPAT_ENDPOINT")
    region = os.getenv("OCI_REGION", "ap-chuncheon-1")

    # Force path-style for maximum compatibility with OCI S3 endpoint.
    config = Config(s3={"addressing_style": "path"})
    return boto3.client(
        "s3",
        region_name=region,
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=config,
    )


def main() -> int:
    try:
        s3 = _make_s3_client()
        target_bucket = _required_env("S3_PORTFOLIO_BUCKET_NAME")

        buckets = s3.list_buckets().get("Buckets", [])
        bucket_names = [bucket["Name"] for bucket in buckets]
        print("Connected to OCI S3-compatible endpoint")
        print(f"Visible buckets: {bucket_names}")

        s3.head_bucket(Bucket=target_bucket)
        print(f"Target bucket is reachable: {target_bucket}")
        return 0
    except ValueError as exc:
        print(f"[CONFIG ERROR] {exc}")
    except ClientError as exc:
        print(f"[OCI ERROR] {exc}")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"[UNEXPECTED ERROR] {exc}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
