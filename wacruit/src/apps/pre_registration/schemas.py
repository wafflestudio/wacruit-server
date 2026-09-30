import base64
import binascii
from pathlib import PurePath
from typing import Literal

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import validator

from wacruit.src.apps.mail.schemas import EmailAttachment

MAX_EMAIL_IMAGE_COUNT = 5
MAX_EMAIL_IMAGE_SIZE_BYTES = 1024 * 1024
_ASCII_CONTROL_END = 32
_ASCII_DELETE = 127
_WEBP_HEADER_LENGTH = 12


class EmailImageAttachmentRequest(BaseModel):
    file_name: str = Field(..., min_length=1, max_length=255)
    content_type: Literal["image/jpeg", "image/png", "image/gif", "image/webp"]
    content_base64: str = Field(..., min_length=1)

    @validator("file_name")
    def validate_file_name(cls, value: str) -> str:
        if PurePath(value).name != value or "/" in value or "\\" in value:
            raise ValueError("파일명에는 경로를 포함할 수 없습니다.")
        if any(
            ord(character) < _ASCII_CONTROL_END or ord(character) == _ASCII_DELETE
            for character in value
        ):
            raise ValueError("파일명에는 제어 문자를 포함할 수 없습니다.")
        return value

    @validator("content_base64")
    def validate_content_base64(cls, value: str, values: dict[str, object]) -> str:
        try:
            content = base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("첨부 이미지가 올바른 Base64 형식이 아닙니다.") from exc
        if len(content) > MAX_EMAIL_IMAGE_SIZE_BYTES:
            raise ValueError("첨부 이미지 한 개의 크기는 1MB 이하여야 합니다.")
        if not cls._matches_image_signature(
            content,
            values.get("content_type"),
        ):
            raise ValueError(
                "첨부 이미지의 실제 형식과 content_type이 일치하지 않습니다."
            )
        return value

    @staticmethod
    def _matches_image_signature(content: bytes, content_type: object) -> bool:
        if content_type == "image/jpeg":
            return content.startswith(b"\xff\xd8\xff")
        if content_type == "image/png":
            return content.startswith(b"\x89PNG\r\n\x1a\n")
        if content_type == "image/gif":
            return content.startswith((b"GIF87a", b"GIF89a"))
        if content_type == "image/webp":
            return (
                len(content) >= _WEBP_HEADER_LENGTH
                and content.startswith(b"RIFF")
                and content[8:12] == b"WEBP"
            )
        return False

    def to_email_attachment(self) -> EmailAttachment:
        return EmailAttachment(
            file_name=self.file_name,
            content_type=self.content_type,
            content=base64.b64decode(self.content_base64, validate=True),
        )


class CreatePreRegistrationRequest(BaseModel):
    url: str
    generation: str
    is_active: bool


class UpdatePreRegistrationRequest(BaseModel):
    url: str | None = None
    generation: str | None = None
    is_active: bool | None = None


class PreRegistrationResponse(BaseModel):
    id: int
    url: str
    generation: str
    is_active: bool

    class Config:
        orm_mode = True


class CreatePreRegistrationUserRequest(BaseModel):
    name: str = Field(..., max_length=50)
    email: EmailStr
    phone_number: str = Field(..., max_length=30)
    university: str | None = Field(default=None, max_length=50)
    college: str | None = Field(default=None, max_length=50)
    department: str | None = Field(default=None, max_length=50)


class PreRegistrationUserResponse(BaseModel):
    id: int
    pre_registration_id: int
    name: str
    email: str
    phone_number: str
    university: str | None
    college: str | None
    department: str | None

    class Config:
        orm_mode = True


class SendPreRegistrationEmailRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    html_content: str | None = None
    attachments: list[EmailImageAttachmentRequest] = Field(
        default_factory=list,
        max_items=MAX_EMAIL_IMAGE_COUNT,
    )
    active_only: bool = True
    pre_registration_id: int | None = None


class SendPreRegistrationEmailResponse(BaseModel):
    status: str
    total_count: int
    queued_count: int
    recipient_limit: int
    is_truncated: bool
