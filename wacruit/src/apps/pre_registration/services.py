from typing import Annotated

from fastapi import BackgroundTasks
from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from wacruit.src.apps.mail.exceptions import MailConfigException
from wacruit.src.apps.mail.exceptions import MailSendFailedException
from wacruit.src.apps.mail.services import EmailService
from wacruit.src.apps.pre_registration.exceptions import PreRegistAlreadyExistException
from wacruit.src.apps.pre_registration.exceptions import PreRegistNotActiveException
from wacruit.src.apps.pre_registration.exceptions import PreRegistNotExistException
from wacruit.src.apps.pre_registration.exceptions import (
    PreRegistUserAlreadyExistException,
)
from wacruit.src.apps.pre_registration.models import PreRegistration
from wacruit.src.apps.pre_registration.models import PreRegistrationUser
from wacruit.src.apps.pre_registration.repositories import PreRegistrationRepository
from wacruit.src.apps.pre_registration.schemas import CreatePreRegistrationRequest
from wacruit.src.apps.pre_registration.schemas import CreatePreRegistrationUserRequest
from wacruit.src.apps.pre_registration.schemas import PreRegistrationUserResponse
from wacruit.src.apps.pre_registration.schemas import SendPreRegistrationEmailRequest
from wacruit.src.apps.pre_registration.schemas import SendPreRegistrationEmailResponse
from wacruit.src.apps.pre_registration.schemas import UpdatePreRegistrationRequest

PRE_REGISTRATION_EMAIL_BATCH_LIMIT = 200


class PreRegistrationService:
    def __init__(
        self,
        pre_registration_repository: Annotated[PreRegistrationRepository, Depends()],
        email_service: Annotated[EmailService, Depends()],
    ):
        self.pre_registration_repository = pre_registration_repository
        self.email_service = email_service

    def check_active_pre_registration(self) -> bool:
        pre_registration = (
            self.pre_registration_repository.get_active_pre_registration()
        )
        if pre_registration is None:
            return False
        return True

    def get_active_pre_registration(self) -> PreRegistration:
        pre_registration = (
            self.pre_registration_repository.get_active_pre_registration()
        )
        if pre_registration is None:
            raise PreRegistNotActiveException()
        return pre_registration

    def get_pre_registration(self) -> list[PreRegistration]:
        pre_registration_list = self.pre_registration_repository.get_pre_registration()
        return pre_registration_list

    def create_pre_registration(
        self, req: CreatePreRegistrationRequest
    ) -> PreRegistration:
        if req.is_active and (self.check_active_pre_registration()):
            raise PreRegistAlreadyExistException()
        to_create = PreRegistration(
            url=req.url, generation=req.generation, is_active=req.is_active
        )
        try:
            pre_registration = self.pre_registration_repository.create_pre_registration(
                to_create
            )
            return pre_registration
        except IntegrityError as exc:
            raise PreRegistAlreadyExistException() from exc

    def update_pre_registration(
        self, pre_registration_id: int, req: UpdatePreRegistrationRequest
    ) -> PreRegistration:
        pre_registration = self.pre_registration_repository.get_pre_registration_by_id(
            pre_registration_id
        )
        if pre_registration is None:
            raise PreRegistNotExistException()

        active_pre_registration = (
            self.pre_registration_repository.get_active_pre_registration()
        )
        if (
            req.is_active
            and active_pre_registration is not None
            and active_pre_registration.id != pre_registration_id
        ):
            raise PreRegistAlreadyExistException()

        for key, value in req.dict(exclude_none=True).items():
            setattr(pre_registration, key, value)
        try:
            return self.pre_registration_repository.update_pre_registration(
                pre_registration
            )
        except IntegrityError as exc:
            raise PreRegistAlreadyExistException() from exc

    def delete_pre_registration(self, pre_registration_id: int) -> None:
        pre_registration = self.pre_registration_repository.get_pre_registration_by_id(
            pre_registration_id
        )
        if pre_registration is None:
            raise PreRegistNotExistException()
        self.pre_registration_repository.delete_pre_registration(pre_registration_id)

    def create_pre_registration_user(
        self, request: CreatePreRegistrationUserRequest
    ) -> PreRegistrationUserResponse:
        pre_registration = self.get_active_pre_registration()
        pre_registration_user = PreRegistrationUser(
            pre_registration_id=pre_registration.id,
            name=request.name,
            email=request.email,
            phone_number=request.phone_number,
            university=request.university,
            college=request.college,
            department=request.department,
        )
        try:
            pre_registration_user = (
                self.pre_registration_repository.create_pre_registration_user(
                    pre_registration_user
                )
            )
        except IntegrityError as exc:
            raise PreRegistUserAlreadyExistException() from exc
        return PreRegistrationUserResponse.from_orm(pre_registration_user)

    def get_pre_registration_users(
        self,
        pre_registration_id: int | None,
        active_only: bool,
        limit: int,
        offset: int,
    ) -> list[PreRegistrationUserResponse]:
        pre_registration_users = (
            self.pre_registration_repository.get_pre_registration_users(
                pre_registration_id=pre_registration_id,
                active_only=active_only,
                limit=limit,
                offset=offset,
            )
        )
        return [
            PreRegistrationUserResponse.from_orm(pre_registration_user)
            for pre_registration_user in pre_registration_users
        ]

    def send_email_to_pre_registration_users(
        self,
        request: SendPreRegistrationEmailRequest,
        background_tasks: BackgroundTasks,
    ) -> SendPreRegistrationEmailResponse:
        pre_registration_users = (
            self.pre_registration_repository.get_pre_registration_users(
                pre_registration_id=request.pre_registration_id,
                active_only=request.active_only,
                limit=PRE_REGISTRATION_EMAIL_BATCH_LIMIT,
                offset=0,
            )
        )
        recipient_emails = [user.email for user in pre_registration_users]

        if recipient_emails:
            background_tasks.add_task(
                self._send_email_to_recipients,
                recipient_emails,
                request.subject,
                request.content,
                request.html_content,
            )

        return SendPreRegistrationEmailResponse(
            status="queued",
            total_count=len(recipient_emails),
            queued_count=len(recipient_emails),
            recipient_limit=PRE_REGISTRATION_EMAIL_BATCH_LIMIT,
        )

    def _send_email_to_recipients(
        self,
        recipient_emails: list[str],
        subject: str,
        content: str,
        html_content: str | None,
    ) -> None:
        for recipient_email in recipient_emails:
            try:
                self.email_service.send_email(
                    to_email=recipient_email,
                    subject=subject,
                    content=content,
                    html_content=html_content,
                )
            except (MailConfigException, MailSendFailedException):
                continue
