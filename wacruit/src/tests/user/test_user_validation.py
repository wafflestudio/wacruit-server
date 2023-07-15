from pydantic import EmailStr
from pydantic import ValidationError
import pytest

from wacruit.src.apps.user.schemas import UserUpdateInvitationEmailsRequest


def test_update_invitation_emails_valid_email():
    UserUpdateInvitationEmailsRequest(
        github_email=EmailStr("github@naver.com"),
        notion_email=EmailStr("notion@naver.com"),
        slack_email=EmailStr("slack@naver.com"),
    )


def test_update_invitation_emails_invalid_email():
    with pytest.raises(ValidationError):
        UserUpdateInvitationEmailsRequest(
            github_email=EmailStr("github@n#$ae@r.com"),
            notion_email=None,
            slack_email=None,
        )
