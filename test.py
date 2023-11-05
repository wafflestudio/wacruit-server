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

# url = s3_client.generate_presigned_url(
#     ClientMethod="get_object",
#     Params={
#         "Bucket": BUCKET_NAME,
#         "Key": "test.txt",
#     },
#     ExpiresIn=1000,
# )
# print(url)
# resp = requests.get(url)
# print(resp)
# print(resp.text)

url = s3_client.generate_presigned_url(
    ClientMethod="put_object",
    Params={
        "Bucket": BUCKET_NAME,
        "Key": "test1/test1.txt",
    },
    ExpiresIn=1000,
)

print(url)

with open("test1.txt", "r") as file:
    content = file.read()
resp = requests.put(url=url, data=content)
print(resp)
print(resp.text)





# resp = requests.put(url)
# print(resp)
# print(resp.text)
# https://wacruit-portfolio.s3.ap-northeast-2.amazonaws.com/test.txt
# https://wacruit-portfolio.s3.amazonaws.com/test.txt?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAV5APOORJET4MZ33S%2F20230720%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20230720T095029Z&X-Amz-Expires=1000&X-Amz-SignedHeaders=host&X-Amz-Signature=d5c05436aaee9204b89d0288e8da6ed825b7858f89a38ea4e40ae656b0e9fab1

# # post
# object_name = "test.txt"
#
# response = s3_client.generate_presigned_post(
#     BUCKET_NAME,
#     object_name,
#     ExpiresIn=3600,
# )
# print(response)
#
# if response is None:
#     exit(1)
#
# # Demonstrate how another Python program can use the presigned URL to upload a file
# with open(object_name, "rb") as f:
#     files = {"file": (object_name, f)}
#     http_response = requests.post(response["url"], data=response["fields"], files=files)
# # If successful, returns HTTP status code 204
# print(http_response)
