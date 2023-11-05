import requests

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError


def generate_presigned_post_url(
    s3_client: BaseClient,
    s3_bucket: str,
    s3_object: str,
    expires_in: int,
    fields: dict | None = None,
    conditions: list[dict | list] | None = None,
):
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
    return response

BUCKET_NAME = "wacruit-portfolio"
OBJECT_NAME = "test1.txt"

s3_client = boto3.client(
    "s3",
    aws_access_key_id="AKIAV5APOORJET4MZ33S",
    aws_secret_access_key="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",
    region_name="ap-northeast-2",
)
#
# resp = generate_presigned_post_url(
#     s3_client=s3_client,
#     s3_bucket=BUCKET_NAME,
#     s3_object=OBJECT_NAME,
#     expires_in=3600,
#     conditions=[
#         # {"acl": "public-read"},
#         # {"bucket": BUCKET_NAME},
#         # ["starts-with", "$Content-Type", "image/"],
#         ["content-length-range", 0, 1024 * 1024],
#         # ["content-length-range", 0, 8],
#     ],
# )
# for k, v in resp.items():
#     print(f"{k}: {v}")
#
# with open(OBJECT_NAME, "rb") as f:
#     files = {"file": (OBJECT_NAME, f)}
#     http_response = requests.post(resp["url"], data=resp["fields"], files=files)
# print(http_response)
# print(http_response.text)


s3_client.delete_object(Bucket=BUCKET_NAME, Key="2/test2.txt")