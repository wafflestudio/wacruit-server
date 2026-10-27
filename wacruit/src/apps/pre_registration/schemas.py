import base64
import binascii
from html.parser import HTMLParser
from pathlib import PurePath
import re
from typing import Literal

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from wacruit.src.apps.mail.schemas import EmailAttachment
from wacruit.src.apps.mail.schemas import EmailInlineImage

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


class EmailInlineImageRequest(EmailImageAttachmentRequest):
    content_id: str = Field(..., min_length=1, max_length=128)

    @validator("content_id")
    def validate_content_id(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.@-]*", value):
            raise ValueError("content_id는 영문, 숫자 및 _.@-만 사용할 수 있습니다.")
        return value

    def to_inline_image(self) -> EmailInlineImage:
        return EmailInlineImage(
            file_name=self.file_name,
            content_type=self.content_type,
            content=base64.b64decode(self.content_base64, validate=True),
            content_id=self.content_id,
        )


class _ImageReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.content_ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "img":
            for name, value in attrs:
                if name == "src" and value and value.lower().startswith("cid:"):
                    self.content_ids.add(value[4:])


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
    content: str = ""
    html_content: str | None = None
    attachments: list[EmailImageAttachmentRequest] = Field(
        default_factory=list,
        max_items=MAX_EMAIL_IMAGE_COUNT,
    )
    inline_images: list[EmailInlineImageRequest] = Field(
        default_factory=list, max_items=MAX_EMAIL_IMAGE_COUNT
    )
    active_only: bool = True
    pre_registration_id: int | None = None

    @root_validator(skip_on_failure=True)
    def validate_body_and_images(cls, values):
        images = values.get("inline_images", [])
        if len(images) + len(values.get("attachments", [])) > MAX_EMAIL_IMAGE_COUNT:
            raise ValueError("첨부 및 인라인 이미지는 합계 5개 이하여야 합니다.")
        ids = [image.content_id for image in images]
        if len(ids) != len(set(ids)):
            raise ValueError("인라인 이미지의 content_id는 중복될 수 없습니다.")
        html = values.get("html_content")
        if images and not (html and html.strip()):
            html = "".join(
                f'<img src="cid:{cid}" style="max-width:100%;height:auto;" alt="">'
                for cid in ids
            )
            values["html_content"] = html
        parser = _ImageReferenceParser()
        parser.feed(html or "")
        if parser.content_ids != set(ids):
            raise ValueError(
                "HTML의 cid 참조와 inline_images의 content_id가 일치해야 합니다."
            )
        if not values.get("content", "").strip() and not (html and html.strip()):
            raise ValueError(
                "텍스트 또는 HTML 본문, 인라인 이미지 중 하나는 필요합니다."
            )
        return values


class SendPreRegistrationEmailResponse(BaseModel):
    status: str
    total_count: int
    queued_count: int
    recipient_limit: int
    is_truncated: bool
