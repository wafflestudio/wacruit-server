from typing import Any

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from wacruit.src.apps.portfolio.aws.s3.method import S3PresignedUrlMethod


def get_list_of_objects(
    s3_client: BaseClient,
    s3_bucket: str,
    s3_prefix: str,
) -> list[str | None]:
    try:
        resp = s3_client.list_objects(
            Bucket=s3_bucket,
            Prefix=s3_prefix,
        )
    except ClientError as e:
        raise RuntimeError("AWS S3 client error") from e
    return [content["Key"] for content in resp["Contents"]]


def delete_object(
    s3_client: BaseClient,
    s3_bucket: str,
    s3_object: str,
):
    try:
        s3_client.delete_object(
            Bucket=s3_bucket,
            Key=s3_object,
        )
    except ClientError as e:
        raise RuntimeError("AWS S3 client error") from e


def generate_presigned_url(
    s3_client: BaseClient,
    client_method: S3PresignedUrlMethod,
    method_parameters: dict[str, Any],
    expires_in: int = 3600,
):
    """
    Generate a presigned Amazon S3 URL that can be used to perform an action.

    :param s3_client: A Boto3 Amazon S3 client.
    :param client_method: The name of the client method that the URL performs.
    :param method_parameters: The parameters of the specified client method.
    :param expires_in: The number of seconds the presigned URL is valid for.
    :return: The presigned URL.
    """
    try:
        url = s3_client.generate_presigned_url(
            ClientMethod=client_method,
            Params=method_parameters,
            ExpiresIn=expires_in
        )
    except ClientError as e:
        raise ValueError(
            f"Couldn't get a presigned URL for client method '{client_method}'"
        ) from e
    return url
