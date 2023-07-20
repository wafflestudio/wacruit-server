from typing import Any

from botocore import client
from botocore import exceptions

from wacruit.src.apps.portfolio.aws import config
from wacruit.src.apps.portfolio.aws.s3 import method


def generate_presigned_url(
    s3_client: client.BaseClient,
    client_method: method.S3PresignedUrlMethod,
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
    except exceptions.ClientError:
        raise exceptions.ClientError("Couldn't get a presigned URL for client method '%s'.", client_method)
    return url


def create_presigned_post(
    s3_client: client.BaseClient,
    object_name: str,
    s3_bucket: str = config.BUCKET_NAME,
    expires_in: int = 3600,
) -> dict:
    """Generate a presigned URL S3 POST request to upload a file

    :param s3_client: A Boto3 Amazon S3 client.
    :param object_name: S3 object name
    :param s3_bucket: Bucket to upload to
    :param expires_in: Time in seconds for the presigned URL to remain valid
    :return response: Dictionary with data required to upload file to S3
    :example usage:
        {
            "url": {{ presigned_url }},
            "fields": {
                "key": {{ object_name }},
                "x-amz-algorithm": ...,
                "x-amz-credential": ...,
                "x-amz-date": ...,
                "policy": ...,
                "x-amz-signature": ...,
            },
        }

    Usage:
    - requests.post(response["url"], data=response["fields"], files=files)
    """
    try:
        response = s3_client.generate_presigned_post(
            Bucket=s3_bucket,
            Key=object_name,
            ExpiresIn=expires_in,
        )
        return response
    except exceptions.ClientError as e:
        raise e
