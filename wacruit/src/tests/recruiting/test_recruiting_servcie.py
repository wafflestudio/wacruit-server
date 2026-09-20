from wacruit.src.apps.common.enums import Language
from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.recruiting.models import RecruitingApplication
from wacruit.src.apps.recruiting.services import RecruitingService
from wacruit.src.apps.user.models import User
from wacruit.src.database.connection import Session


def test_get_all_recruiting(
    recruiting_service: RecruitingService, recruiting: Recruiting
):
    recruiting_list = recruiting_service.get_all_recruiting()
    recruiting_applicant_dto = recruiting_list.items[0]
    assert recruiting_applicant_dto.id == recruiting.id
    assert recruiting_applicant_dto.name == recruiting.name
    assert recruiting_applicant_dto.is_active == recruiting.is_active
    assert recruiting_applicant_dto.from_date == recruiting.from_date
    assert recruiting_applicant_dto.to_date == recruiting.to_date
    assert recruiting_applicant_dto.short_description == recruiting.short_description


def test_get_recruiting_by_id(
    recruiting_service: RecruitingService, recruiting: Recruiting, user: User
):
    recruiting_response = recruiting_service.get_user_recruiting_by_id(
        recruiting.id, user
    )
    assert recruiting_response.name == recruiting.name
    assert recruiting_response.is_active == recruiting.is_active
    assert recruiting_response.from_date == recruiting.from_date
    assert recruiting_response.to_date == recruiting.to_date
    assert recruiting_response.description == recruiting.description

    problems = recruiting_response.problem_status
    assert len(problems) == 1


def test_get_recruiting_submissions_excludes_code_only_user(
    db_session: Session,
    recruiting_service: RecruitingService,
    recruiting: Recruiting,
    user: User,
):
    code_only_user = User(
        sso_id="code-only",
        first_name="test",
        last_name="user",
        phone_number="010-1111-1111",
        email="code-only@example.com",
        is_admin=False,
    )
    db_session.add(code_only_user)
    db_session.flush()

    db_session.add_all(
        [
            RecruitingApplication(user_id=user.id, recruiting_id=recruiting.id),
            CodeSubmission(
                user_id=code_only_user.id,
                problem_id=recruiting.problems[0].id,
                language=Language.PYTHON,
                source_code="print('submitted without applying')",
            ),
        ]
    )
    db_session.commit()

    response = recruiting_service.get_recruiting_submissions(
        recruiting_id=recruiting.id, limit=100, offset=0
    )

    assert response.applicant_count == 1
    assert len(response.items) == 1
    assert response.items[0].first_name == user.first_name
    assert response.items[0].last_name == user.last_name
