import requests

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "waffle-user-id": "test1",
}
#
resp = requests.delete(
    url="http://127.0.0.1:8080/api/v1/portfolios/url/1",
    headers=headers,
)

print(resp)
print(resp.json())
#
# resp = requests.get(
#     url="http://127.0.0.1:8080/api/v1/portfolios/url",
#     headers=headers,
# )
#
# print(resp)
# print(resp.json())

# resp = requests.post(
#     url="http://127.0.0.1:8080/api/v1/portfolios/url?url=https://www.google.com",
#     headers=headers,
# )
# print(resp)
# print(resp.json())
#
# resp = requests.get(
#     url="http://127.0.0.1:8080/api/v1/portfolios/url",
#     headers=headers,
# )
#
# print(resp)
# print(resp.json())
