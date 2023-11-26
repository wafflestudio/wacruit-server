from typing import Any

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from wacruit.src.apps.portfolio.file.aws.s3.method import S3PresignedUrlMethod


def get_list_of_objects(
    s3_client: BaseClient,
    s3_bucket: str,
    s3_prefix: str,
) -> list[str]:
    try:
        resp = s3_client.list_objects(
            Bucket=s3_bucket,
            Prefix=s3_prefix,
        )
    except ClientError as e:
        raise RuntimeError("AWS S3 client error") from e
    if "Contents" not in resp.keys():
        return []
    return [content["Key"] for content in resp["Contents"]]


def delete_object(
    s3_client: BaseClient,
    s3_bucket: str,
    s3_object: str,
) -> None:
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
    expires_in: int,
) -> str:
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
            ClientMethod=client_method, Params=method_parameters, ExpiresIn=expires_in
        )
    except ClientError as e:
        raise RuntimeError("AWS S3 client error") from e
    return url


def generate_presigned_post_url(
    s3_client: BaseClient,
    s3_bucket: str,
    s3_object: str,
    expires_in: int,
    fields: dict | None = None,
    conditions: list[dict | list] | None = None,
) -> tuple[str, dict]:
    """Generate a presigned URL S3 POST request to upload a file

    :param s3_client: boto3 S3 client
    :param s3_bucket: s3 bucket name
    :param s3_object: s3 object name
    :param expires_in: Time in seconds for the presigned URL to remain valid
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    try:
        response = s3_client.generate_presigned_post(
            s3_bucket,
            s3_object,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=expires_in,
        )
    except ClientError as e:
        raise RuntimeError("AWS S3 client error") from e

    # The response contains the presigned URL and required fields
    return response["url"], response["fields"]
