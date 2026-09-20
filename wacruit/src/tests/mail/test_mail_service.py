from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from typing import cast

import pytest

from wacruit.src.apps.mail import services as mail_services
from wacruit.src.apps.mail.config import mail_config
from wacruit.src.apps.mail.exceptions import MailConfigException
from wacruit.src.apps.mail.exceptions import MailSendFailedException
from wacruit.src.apps.mail.schemas import EmailAttachment
from wacruit.src.apps.mail.services import EmailService


class FakeEmailClient:
    def __init__(self) -> None:
        self.submitted = []

    def submit_email(self, submit_email_details):
        self.submitted.append(submit_email_details)

    def submit_raw_email(self, **kwargs):
        self.submitted.append(kwargs)


@pytest.fixture(autouse=True)
def reset_mail_config(monkeypatch):
    monkeypatch.setattr(mail_config, "compartment_id", "")
    monkeypatch.setattr(mail_config, "from_email", "")
    monkeypatch.setattr(mail_config, "from_name", "")
    monkeypatch.setattr(mail_config, "reply_to", "")
    monkeypatch.setattr(mail_config, "service_endpoint", "")


def test_send_email_raises_when_required_config_is_missing():
    with pytest.raises(MailConfigException):
        EmailService().send_email(
            to_email="to@example.com",
            subject="subject",
            content="content",
        )


@pytest.mark.parametrize(
    "from_email",
    [
        "no-reply",
        "no-reply@",
        "@example.com",
        "no-reply@example@com",
        " no-reply@example.com",
        "no-reply@example.com ",
        "no reply@example.com",
        "no-reply@exa mple.com",
        "no-reply@example.com\nbcc@example.com",
    ],
)
def test_send_email_raises_when_from_email_is_invalid(monkeypatch, from_email):
    fake_client = FakeEmailClient()
    monkeypatch.setattr(mail_config, "compartment_id", "ocid1.compartment.oc1..test")
    monkeypatch.setattr(mail_config, "from_email", from_email)

    service = EmailService()
    service._client = fake_client  # type: ignore[assignment]

    with pytest.raises(MailConfigException) as exc_info:
        service.send_email(
            to_email="to@example.com",
            subject="subject",
            content="content",
        )

    assert exc_info.value.detail == "메일 발신자 주소 형식이 올바르지 않습니다."
    assert fake_client.submitted == []


def test_send_email_submits_oci_email_payload(monkeypatch):
    fake_client = FakeEmailClient()
    monkeypatch.setattr(mail_config, "compartment_id", "ocid1.compartment.oc1..test")
    monkeypatch.setattr(mail_config, "from_email", "no-reply@example.com")
    monkeypatch.setattr(mail_config, "from_name", "Waffle Studio")
    monkeypatch.setattr(mail_config, "reply_to", "help@example.com")

    service = EmailService()
    service._client = fake_client  # type: ignore[assignment]

    service.send_email(
        to_email="to@example.com",
        subject="subject",
        content="content",
    )

    [details] = fake_client.submitted
    assert details.sender.compartment_id == "ocid1.compartment.oc1..test"
    assert details.sender.sender_address.email == "no-reply@example.com"
    assert details.sender.sender_address.name == "Waffle Studio"
    assert details.recipients.to[0].email == "to@example.com"
    assert details.reply_to[0].email == "help@example.com"
    assert details.subject == "subject"
    assert details.body_text == "content"
    assert details.body_html is None
    assert details.message_id.endswith("@example.com")
    assert not details.message_id.startswith("<")
    assert not details.message_id.endswith(">")


def test_send_password_reset_code_submits_text_and_html_body(monkeypatch):
    fake_client = FakeEmailClient()
    monkeypatch.setattr(mail_config, "compartment_id", "ocid1.compartment.oc1..test")
    monkeypatch.setattr(mail_config, "from_email", "no-reply@example.com")

    service = EmailService()
    service._client = fake_client  # type: ignore[assignment]

    service.send_password_reset_code("to@gmail.com", "123456")

    [details] = fake_client.submitted
    assert details.recipients.to[0].email == "to@gmail.com"
    assert details.subject == "[Waffle Studio] 비밀번호 재설정 인증번호"
    assert "인증번호: 123456" in details.body_text
    assert "인증번호는 5분 동안 유효합니다." in details.body_text
    assert "<strong>인증번호: 123456</strong>" in details.body_html
    assert "<p>인증번호는 5분 동안 유효합니다.</p>" in details.body_html


def test_send_email_submits_mime_payload_with_image_attachment(monkeypatch):
    fake_client = FakeEmailClient()
    monkeypatch.setattr(mail_config, "compartment_id", "ocid1.compartment.oc1..test")
    monkeypatch.setattr(mail_config, "from_email", "no-reply@example.com")
    monkeypatch.setattr(mail_config, "from_name", "Waffle Studio")
    monkeypatch.setattr(mail_config, "reply_to", "help@example.com")

    service = EmailService()
    service._client = fake_client  # type: ignore[assignment]

    service.send_email(
        to_email="to@example.com",
        subject="이미지 첨부 테스트",
        content="텍스트 본문",
        html_content="<p>HTML 본문</p>",
        attachments=[
            EmailAttachment(
                file_name="poster.png",
                content_type="image/png",
                content=b"\x89PNG\r\n\x1a\nimage-data",
            )
        ],
    )

    [submitted] = fake_client.submitted
    assert submitted["content_type"] == "message/rfc822"
    assert submitted["compartment_id"] == "ocid1.compartment.oc1..test"
    assert submitted["sender"] == "no-reply@example.com"
    assert submitted["recipients"] == ["to@example.com"]

    raw_message = submitted["raw_message"].read()
    assert submitted["content_length"] == len(raw_message)
    message = cast(
        EmailMessage,
        BytesParser(policy=policy.default).parsebytes(raw_message),
    )
    assert message["From"] == "Waffle Studio <no-reply@example.com>"
    assert message["To"] == "to@example.com"
    assert message["Reply-To"] == "help@example.com"
    assert message["Subject"] == "이미지 첨부 테스트"

    attachment = next(message.iter_attachments())
    assert attachment.get_filename() == "poster.png"
    assert attachment.get_content_type() == "image/png"
    assert attachment.get_payload(decode=True) == b"\x89PNG\r\n\x1a\nimage-data"


def test_send_email_rejects_raw_message_over_oci_size_limit(monkeypatch):
    fake_client = FakeEmailClient()
    monkeypatch.setattr(mail_config, "compartment_id", "ocid1.compartment.oc1..test")
    monkeypatch.setattr(mail_config, "from_email", "no-reply@example.com")
    monkeypatch.setattr(mail_services, "MAX_RAW_EMAIL_SIZE_BYTES", 10)

    service = EmailService()
    service._client = fake_client  # type: ignore[assignment]

    with pytest.raises(MailSendFailedException):
        service.send_email(
            to_email="to@example.com",
            subject="subject",
            content="content",
            attachments=[
                EmailAttachment(
                    file_name="poster.png",
                    content_type="image/png",
                    content=b"\x89PNG\r\n\x1a\nimage-data",
                )
            ],
        )

    assert fake_client.submitted == []
