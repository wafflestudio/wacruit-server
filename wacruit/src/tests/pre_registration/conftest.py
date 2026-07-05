from typing import List

import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.mail.exceptions import MailSendFailedException
from wacruit.src.apps.mail.services import EmailService
from wacruit.src.apps.pre_registration.models import PreRegistration
from wacruit.src.apps.pre_registration.repositories import PreRegistrationRepository
from wacruit.src.apps.pre_registration.schemas import CreatePreRegistrationRequest
from wacruit.src.apps.pre_registration.schemas import UpdatePreRegistrationRequest
from wacruit.src.apps.pre_registration.services import PreRegistrationService
from wacruit.src.database.connection import Transaction


class FakeEmailService(EmailService):
    def __init__(self) -> None:
        self.sent_emails: list[tuple[str, str, str, str | None]] = []
        self.failed_emails: set[str] = set()

    def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: str | None = None,
    ) -> None:
        if to_email in self.failed_emails:
            raise MailSendFailedException()
        self.sent_emails.append((to_email, subject, content, html_content))


@pytest.fixture
def pre_registration_repository(db_session: Session) -> PreRegistrationRepository:
    return PreRegistrationRepository(
        session=db_session, transaction=Transaction(db_session)
    )


@pytest.fixture
def fake_email_service() -> FakeEmailService:
    return FakeEmailService()


@pytest.fixture
def pre_registration_service(
    pre_registration_repository: PreRegistrationRepository,
    fake_email_service: FakeEmailService,
) -> PreRegistrationService:
    return PreRegistrationService(
        pre_registration_repository=pre_registration_repository,
        email_service=fake_email_service,
    )


@pytest.fixture
def created_active_pre_registration(
    db_session: Session,
):
    pre_registration = PreRegistration(
        url="https://wafflestudio.com/24_5_pre_registration",
        generation="24.5",
        is_active=True,
    )
    db_session.add(pre_registration)
    db_session.commit()
    return pre_registration


@pytest.fixture
def created_no_active_pre_registration(
    db_session: Session,
):
    pre_registration = PreRegistration(
        url="https://wafflestudio.com/23_5_pre_registration",
        generation="23.5",
        is_active=False,
    )
    db_session.add(pre_registration)
    db_session.commit()
    return pre_registration


@pytest.fixture
def created_pre_registration_list(db_session: Session) -> List[PreRegistration]:
    pre_registration_list = []
    for i in range(4):
        pre_registration = PreRegistration(
            url=f"https://wafflestudio.com/{i}_5_pre_registration",
            generation=f"{i + 20}.5",
            is_active=False,
        )
        db_session.add(pre_registration)
        pre_registration_list.append(pre_registration)

    pre_registration = PreRegistration(
        url="https://wafflestudio.com/24_5_pre_registration",
        generation="24.5",
        is_active=True,
    )
    pre_registration_list.append(pre_registration)
    db_session.add(pre_registration)
    db_session.commit()
    return pre_registration_list


@pytest.fixture
def pre_registration_create_dto() -> CreatePreRegistrationRequest:
    return CreatePreRegistrationRequest(
        url="https://wafflestudio.com/24_5_pre_registration",
        generation="24.5",
        is_active=True,
    )


@pytest.fixture
def pre_registration_update_dto() -> UpdatePreRegistrationRequest:
    return UpdatePreRegistrationRequest(
        url="https://wafflestudio.com/23_5_pre_registration",
        generation="23.5",
        is_active=False,
    )
