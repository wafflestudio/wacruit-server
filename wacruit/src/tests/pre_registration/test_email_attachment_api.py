import base64
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from http import HTTPStatus
from types import SimpleNamespace
from typing import cast
from unittest.mock import create_autospec

from fastapi import FastAPI
from fastapi.testclient import TestClient
from oci.email_data_plane import EmailDPClient
import pytest

from wacruit.src.apps.mail.config import mail_config
from wacruit.src.apps.mail.services import EmailService
from wacruit.src.apps.pre_registration.repositories import PreRegistrationRepository
from wacruit.src.apps.pre_registration.services import PreRegistrationService
from wacruit.src.apps.pre_registration.views import v3_router
from wacruit.src.apps.user.dependencies import get_admin_user

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8"
    "/x8AAwMCAO+aD1sAAAAASUVORK5CYII="
)
RECIPIENTS = ["first@example.com", "second@example.com"]


@pytest.fixture
def email_api(monkeypatch):
    monkeypatch.setattr(mail_config, "compartment_id", "ocid1.compartment.oc1..test")
    monkeypatch.setattr(mail_config, "from_email", "no-reply@example.com")
    monkeypatch.setattr(mail_config, "from_name", "Waffle Studio")
    monkeypatch.setattr(mail_config, "reply_to", "")
    repository = create_autospec(PreRegistrationRepository, instance=True)
    repository.count_pre_registration_users.return_value = 2
    repository.get_pre_registration_users.return_value = [
        SimpleNamespace(email=recipient) for recipient in RECIPIENTS
    ]
    oci_client = create_autospec(EmailDPClient, instance=True)
    email_service = EmailService()
    email_service._client = oci_client
    service = PreRegistrationService(repository, email_service)
    app = FastAPI()
    app.include_router(v3_router)
    app.dependency_overrides[get_admin_user] = lambda: SimpleNamespace(is_admin=True)
    app.dependency_overrides[PreRegistrationService] = lambda: service
    with TestClient(app) as client:
        yield client, oci_client


def test_email_api_preserves_images_and_bodies_for_each_recipient(email_api):
    client, oci_client = email_api
    filenames = ["행사 포스터.png", "second.png"]
    response = client.post(
        "/v3/pre-registration/users/email",
        json={
            "subject": "이미지 첨부 테스트",
            "content": "텍스트 본문",
            "html_content": "<p>HTML 본문</p>",
            "attachments": [
                {
                    "file_name": filename,
                    "content_type": "image/png",
                    "content_base64": base64.b64encode(PNG).decode(),
                }
                for filename in filenames
            ],
        },
    )
    assert response.status_code == HTTPStatus.ACCEPTED
    assert response.json()["queued_count"] == len(RECIPIENTS)
    oci_client.submit_email.assert_not_called()
    calls = oci_client.submit_raw_email.call_args_list
    assert len(calls) == len(RECIPIENTS)
    for call, recipient in zip(calls, RECIPIENTS):
        payload = call.kwargs
        assert payload["recipients"] == [recipient]
        raw = payload["raw_message"].getvalue()
        assert payload["content_length"] == len(raw)
        message = cast(EmailMessage, BytesParser(policy=policy.default).parsebytes(raw))
        assert message["To"] == recipient
        assert message["Subject"] == "이미지 첨부 테스트"
        plain_body = message.get_body(preferencelist=("plain",))
        html_body = message.get_body(preferencelist=("html",))
        assert plain_body is not None
        assert html_body is not None
        assert plain_body.get_content().strip() == "텍스트 본문"
        assert html_body.get_content().strip() == "<p>HTML 본문</p>"
        attachments = list(message.iter_attachments())
        assert [part.get_filename() for part in attachments] == filenames
        assert all(part.get_payload(decode=True) == PNG for part in attachments)


def test_email_api_rejects_invalid_image_before_submission(email_api):
    client, oci_client = email_api
    response = client.post(
        "/v3/pre-registration/users/email",
        json={
            "subject": "test",
            "content": "body",
            "attachments": [
                {
                    "file_name": "poster.png",
                    "content_type": "image/png",
                    "content_base64": base64.b64encode(b"not an image").decode(),
                }
            ],
        },
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    oci_client.submit_raw_email.assert_not_called()
    oci_client.submit_email.assert_not_called()


def test_email_api_without_attachments_uses_existing_submission(email_api):
    client, oci_client = email_api
    response = client.post(
        "/v3/pre-registration/users/email",
        json={"subject": "test", "content": "body"},
    )
    assert response.status_code == HTTPStatus.ACCEPTED
    assert oci_client.submit_email.call_count == len(RECIPIENTS)
    oci_client.submit_raw_email.assert_not_called()
