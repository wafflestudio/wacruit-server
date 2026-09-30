import base64

from pydantic import ValidationError
import pytest

from wacruit.src.apps.pre_registration.schemas import MAX_EMAIL_IMAGE_COUNT
from wacruit.src.apps.pre_registration.schemas import MAX_EMAIL_IMAGE_SIZE_BYTES
from wacruit.src.apps.pre_registration.schemas import EmailImageAttachmentRequest
from wacruit.src.apps.pre_registration.schemas import SendPreRegistrationEmailRequest


def test_email_image_attachment_decodes_base64_content():
    content = b"\x89PNG\r\n\x1a\nimage-data"
    attachment = EmailImageAttachmentRequest(
        file_name="poster.png",
        content_type="image/png",
        content_base64=base64.b64encode(content).decode(),
    )

    email_attachment = attachment.to_email_attachment()

    assert email_attachment.file_name == "poster.png"
    assert email_attachment.content_type == "image/png"
    assert email_attachment.content == content


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("file_name", "../poster.png"),
        ("file_name", "folder\\poster.png"),
        ("content_type", "application/pdf"),
        ("content_base64", "not-base64!"),
    ],
)
def test_email_image_attachment_rejects_invalid_input(field, value):
    data = {
        "file_name": "poster.png",
        "content_type": "image/png",
        "content_base64": base64.b64encode(b"\x89PNG\r\n\x1a\nimage").decode(),
    }
    data[field] = value

    with pytest.raises(ValidationError):
        EmailImageAttachmentRequest.parse_obj(data)


def test_email_image_attachment_rejects_oversized_image():
    with pytest.raises(ValidationError) as exc_info:
        EmailImageAttachmentRequest(
            file_name="poster.png",
            content_type="image/png",
            content_base64=base64.b64encode(
                b"\x89PNG\r\n\x1a\n" + b"x" * MAX_EMAIL_IMAGE_SIZE_BYTES
            ).decode(),
        )

    assert "1MB" in str(exc_info.value)


def test_email_image_attachment_rejects_mismatched_content_type():
    with pytest.raises(ValidationError) as exc_info:
        EmailImageAttachmentRequest(
            file_name="poster.png",
            content_type="image/png",
            content_base64=base64.b64encode(b"GIF89aimage-data").decode(),
        )

    assert "실제 형식" in str(exc_info.value)


def test_send_email_request_rejects_too_many_images():
    attachment = {
        "file_name": "poster.png",
        "content_type": "image/png",
        "content_base64": base64.b64encode(b"\x89PNG\r\n\x1a\nimage").decode(),
    }

    with pytest.raises(ValidationError):
        SendPreRegistrationEmailRequest.parse_obj(
            {
                "subject": "subject",
                "content": "content",
                "attachments": [attachment] * (MAX_EMAIL_IMAGE_COUNT + 1),
            }
        )
