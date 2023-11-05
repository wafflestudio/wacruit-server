import boto3
import requests
import json
ACCESS_KEY = "AKIAV5APOORJET4MZ33S"
SECRET_KEY = "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"
BUCKET_NAME = "wacruit-portfolio"

s3_client = boto3.client(
    "s3",
    aws_access_key_id="AKIAV5APOORJET4MZ33S",
    aws_secret_access_key="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",
    region_name="ap-northeast-2",
)

user = "test1"
resp = s3_client.list_objects(
    Bucket=BUCKET_NAME,
    Prefix=f"{user}/",
)

print(resp)
contents = resp["Contents"]
print(contents)
portfolios = [content["Key"][len(user) + 1:] for content in contents]
print(portfolios)