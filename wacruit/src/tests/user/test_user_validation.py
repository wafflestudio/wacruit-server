from email_validator import EmailNotValidError
from fastapi import HTTPException
from pydantic import ValidationError
import pytest

from wacruit.src.apps.user.exceptions import UserAlreadyExistsException
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.repositories import UserRepository
from wacruit.src.apps.user.schemas import UserCreateUpdateRequest
from wacruit.src.apps.user.schemas import UserUpdateInvitationEmailsRequest
from wacruit.src.apps.user.services import UserService


def test_update_invitation_emails_valid_email():
    UserUpdateInvitationEmailsRequest(
        github_email="github@naver.com",
        notion_email="notion@naver.com",
        slack_email="slack@naver.com",
    )


def test_update_invitation_emails_invalid_email():
    with pytest.raises(ValidationError):
        UserUpdateInvitationEmailsRequest(
            github_email="github@n#$ae@r.com",
            notion_email=None,
            slack_email=None,
        )


def test_update_invitation_emails_indeliverable_email():
    with pytest.raises(ValidationError):
        UserUpdateInvitationEmailsRequest(
            github_email="github@nazver.invalidroot",
            notion_email=None,
            slack_email=None,
        )
