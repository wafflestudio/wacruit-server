import requests

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "waffle-user-id": "test2",
}
#
resp = requests.post(
    url="http://127.0.0.1:8080/api/v1/portfolios/url/?url=https://www.google.com",
    headers=headers,
)
# resp = requests.post(
#     url="http://127.0.0.1:8080/api/v1/portfolios/url/?url=https://www.google.com",
#     headers=headers,
# )
print(resp.text, resp)
print(resp.headers)