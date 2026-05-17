from email.message import EmailMessage
import smtplib

from wacruit.src.apps.mail.config import mail_config
from wacruit.src.apps.mail.exceptions import MailConfigException
from wacruit.src.apps.mail.exceptions import MailSendFailedException


class EmailService:
    def send_password_reset_code(self, to_email: str, code: str) -> None:
        subject = "[Waffle Studio] 비밀번호 재설정 인증 번호"
        content = (
            "비밀번호 재설정을 위한 인증 번호입니다.\n\n"
            f"인증 번호: {code}\n\n"
            "인증 번호는 10분 동안 유효합니다."
        )
        self.send_email(to_email=to_email, subject=subject, content=content)

    def send_email(self, to_email: str, subject: str, content: str) -> None:
        if not (
            mail_config.host
            and mail_config.port
            and mail_config.username
            and mail_config.password
            and mail_config.from_email
        ):
            raise MailConfigException()

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = mail_config.from_email
        message["To"] = to_email
        message.set_content(content)

        try:
            with smtplib.SMTP(
                mail_config.host,
                mail_config.port,
                timeout=mail_config.timeout,
            ) as smtp:
                if mail_config.use_tls:
                    smtp.starttls()
                smtp.login(mail_config.username, mail_config.password)
                smtp.send_message(message)
        except (OSError, smtplib.SMTPException) as exc:
            raise MailSendFailedException() from exc
