from email.message import EmailMessage
from email.policy import SMTP
from email.utils import formataddr
from html import escape
from io import BytesIO
from typing import Optional
import uuid

import oci
from oci.email_data_plane import EmailDPClient
from oci.email_data_plane.models import EmailAddress
from oci.email_data_plane.models import Recipients
from oci.email_data_plane.models import Sender
from oci.email_data_plane.models import SubmitEmailDetails
from oci.exceptions import BaseRequestException
from oci.exceptions import InvalidConfig
from oci.exceptions import ServiceError

from wacruit.src.apps.mail.config import mail_config
from wacruit.src.apps.mail.exceptions import MailConfigException
from wacruit.src.apps.mail.exceptions import MailSendFailedException
from wacruit.src.apps.mail.schemas import EmailAttachment
from wacruit.src.settings import settings

MAX_RAW_EMAIL_SIZE_BYTES = 2 * 1024 * 1024


class EmailService:
    def __init__(self) -> None:
        self._client: Optional[EmailDPClient] = None

    def send_password_reset_code(self, to_email: str, code: str) -> None:
        subject = "[Waffle Studio] 비밀번호 재설정 인증번호"
        content = (
            "비밀번호 재설정을 위한 인증번호입니다.\n\n"
            f"인증번호: {code}\n\n"
            "인증번호는 5분 동안 유효합니다."
        )
        html_content = (
            "<p>비밀번호 재설정을 위한 인증번호입니다.</p>"
            f"<p><strong>인증번호: {escape(code)}</strong></p>"
            "<p>인증번호는 5분 동안 유효합니다.</p>"
        )
        self.send_email(
            to_email=to_email,
            subject=subject,
            content=content,
            html_content=html_content,
        )

    def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: str | None = None,
        attachments: list[EmailAttachment] | None = None,
    ) -> None:
        if not mail_config.compartment_id or not mail_config.from_email:
            raise MailConfigException()
        if not self._is_valid_from_email(mail_config.from_email):
            raise MailConfigException("메일 발신자 주소 형식이 올바르지 않습니다.")

        sender_address = EmailAddress(email=mail_config.from_email)
        if mail_config.from_name:
            sender_address.name = mail_config.from_name

        try:
            if attachments:
                self._submit_email_with_attachments(
                    to_email=to_email,
                    subject=subject,
                    content=content,
                    html_content=html_content,
                    attachments=attachments,
                )
                return

            self._get_client().submit_email(
                SubmitEmailDetails(
                    message_id=self._generate_message_id(),
                    sender=Sender(
                        sender_address=sender_address,
                        compartment_id=mail_config.compartment_id,
                    ),
                    recipients=Recipients(to=[EmailAddress(email=to_email)]),
                    subject=subject,
                    body_text=content,
                    body_html=html_content,
                    reply_to=(
                        [EmailAddress(email=mail_config.reply_to)]
                        if mail_config.reply_to
                        else None
                    ),
                )
            )
        except (
            BaseRequestException,
            InvalidConfig,
            OSError,
            ServiceError,
            ValueError,
        ) as exc:
            raise MailSendFailedException() from exc

    def _submit_email_with_attachments(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: str | None,
        attachments: list[EmailAttachment],
    ) -> None:
        message = EmailMessage()
        message["Message-ID"] = f"<{self._generate_message_id()}>"
        message["From"] = (
            formataddr((mail_config.from_name, mail_config.from_email))
            if mail_config.from_name
            else mail_config.from_email
        )
        message["To"] = to_email
        message["Subject"] = subject
        if mail_config.reply_to:
            message["Reply-To"] = mail_config.reply_to

        message.set_content(content)
        if html_content is not None:
            message.add_alternative(html_content, subtype="html")

        for attachment in attachments:
            _, subtype = attachment.content_type.split("/", maxsplit=1)
            message.add_attachment(
                attachment.content,
                maintype="image",
                subtype=subtype,
                filename=attachment.file_name,
            )

        raw_message = message.as_bytes(policy=SMTP)
        if len(raw_message) > MAX_RAW_EMAIL_SIZE_BYTES:
            raise ValueError("메일 본문과 첨부파일의 전체 크기는 2MB 이하여야 합니다.")

        self._get_client().submit_raw_email(
            content_type="message/rfc822",
            compartment_id=mail_config.compartment_id,
            sender=mail_config.from_email,
            recipients=[to_email],
            raw_message=BytesIO(raw_message),
            content_length=len(raw_message),
        )

    def _get_client(self) -> EmailDPClient:
        if self._client is not None:
            return self._client

        client_kwargs: dict[str, object] = {"timeout": mail_config.timeout}
        if mail_config.service_endpoint:
            client_kwargs["service_endpoint"] = mail_config.service_endpoint

        try:
            signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        except Exception:  # noqa: PLW0718
            if not (settings.is_local or settings.is_test):
                raise
            config = oci.config.from_file()
            self._client = EmailDPClient(config, **client_kwargs)
        else:
            self._client = EmailDPClient(
                {"region": settings.oci_region},
                signer=signer,
                **client_kwargs,
            )

        return self._client

    def _generate_message_id(self) -> str:
        domain = mail_config.from_email.rsplit("@", 1)[-1]
        return f"{uuid.uuid4()}@{domain}"

    def _is_valid_from_email(self, email: str) -> bool:
        if email != email.strip() or any(char.isspace() for char in email):
            return False
        if email.count("@") != 1:
            return False
        local_part, separator, domain = email.partition("@")
        return bool(local_part and separator and domain and "@" not in domain)
