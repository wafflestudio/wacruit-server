import requests

resp = requests.post(
    url="http://127.0.0.1:8080/api/v1/users",
    headers={
        "Content-Type": "application/json; charset=utf-8",
        "waffle-user-id": "test2",
    },
    json={
        "first_name": "test2",
        "last_name": "test2",
        "phone_number": "020-2222-2222",
        "email": "test2@example.com",
    }
)

print(resp)
print(resp.text)
