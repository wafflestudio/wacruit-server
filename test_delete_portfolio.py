import requests

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "waffle-user-id": "test6",
}
#
resp = requests.delete(
    url="http://127.0.0.1:8080/api/v1/portfolios/file/delete/?file_name=test.png",
    headers=headers,
)

print(resp, resp.text)
print(resp.json())

# url = resp.json()["presigned_url"]
# print(url)
#
# resp = requests.get(
#     url=url,
# )
# print(resp)
# print(resp.text)
