import requests

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "waffle-user-id": "test6",
}

resp = requests.get(
    url="http://127.0.0.1:8080/api/v1/portfolios/stat/",
    headers=headers,
)
#
# # resp = requests.get(
# #     url="http://127.0.0.1:8080/api/v1/portfolios/url/download/test.txt",
# #     headers=headers,
# # )
#
print(resp)
print(resp.json())

# url = resp.json()["presigned_url"]
# print(url)
#
# resp = requests.get(
#     url=url,
# )
# print(resp)
# print(resp.text)
# import boto3
#
# client = boto3.client(
#     "s3", region_name="ap-northeast-2",
#     aws_access_key_id="AKIAV5APOORJGPRMAQO4",
#     aws_secret_access_key="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",)
#
# resp = client.list_objects(Bucket="wacruit-portfolio-dev")
# print(resp["Contents"])