import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from wacruit.src.apps.common.security import PasswordService
from wacruit.src.apps.user.models import User


def test_create_user(db_session: Session, user: User):
    db_session.add(user)
    db_session.flush()

    users = db_session.query(User).all()
    assert len(users) == 1
    assert users[0].first_name == "Test"


def test_create_user_with_same_email(db_session: Session, user: User):
    db_session.add(user)
    db_session.flush()

    users = db_session.query(User).all()
    assert len(users) == 1
    assert users[0].first_name == "Test"

    user = User(
        sso_id=user.sso_id,
        first_name="Test",
        last_name="User",
        phone_number="010-0000-0000",
        email="test@test.com",
        is_admin=False,
        password=PasswordService.hash_password("password123"),
    )

    db_session.add(user)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_db_session_add_same_object_twice(db_session: Session, user: User):
    db_session.add(user)
    db_session.flush()

    db_session.add(user)
    db_session.flush()

    users = db_session.query(User).all()
    assert len(users) == 1
