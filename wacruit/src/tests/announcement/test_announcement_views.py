from fastapi.testclient import TestClient

from wacruit.src.apps.user.models import User


def test_cant_create_announcement_if_not_admin(user: User, test_client: TestClient):
    assert user.is_admin is False
    token_response = test_client.post(
        "/api/v3/auth/login", json={"username": "name", "password": "password123"}
    ).json()
    response = test_client.post(
        "/api/v1/announcements/",
        json={
            "title": "title",
            "content": "content",
        },
        headers={"Authorization": f"Bearer {token_response['access_token']}"},
    )
    assert response.status_code == 403


def test_can_create_announcement_if_admin(admin_user: User, test_client: TestClient):
    assert admin_user.is_admin is True
    token_res = test_client.post(
        "/api/v3/auth/login", json={"username": "admin", "password": "password123"}
    ).json()
    response = test_client.post(
        "/api/v1/announcements/",
        json={
            "title": "title",
            "content": "content",
        },
        headers={"Authorization": f"Bearer {token_res['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "title"
    assert response.json()["content"] == "content"
