import requests

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "waffle-user-id": "test2",
}
#
resp = requests.get(
    url="http://127.0.0.1:8080/api/v1/portfolios/url/upload/test2.txt",
    headers=headers,
)

print(resp)
print(resp.json())
#
url = resp.json()["presigned_url"]
fields = resp.json()["fields"]
# print(url)
#
OBJECT_NAME = "test1.txt"
with open(OBJECT_NAME, "r") as file:
    files = {"file": (OBJECT_NAME, file)}
    http_response = requests.post(
        url=url,
        data=fields,
        files=files
    )
print(http_response)
print(http_response.text)
