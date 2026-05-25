import pytest

from wacruit.src.apps.mail.config import mail_config
from wacruit.src.apps.mail.exceptions import MailConfigException
from wacruit.src.apps.mail.services import EmailService


class FakeEmailClient:
    def __init__(self) -> None:
        self.submitted = []

    def submit_email(self, submit_email_details):
        self.submitted.append(submit_email_details)


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
    assert details.message_id.startswith("<")
    assert details.message_id.endswith("@example.com>")
