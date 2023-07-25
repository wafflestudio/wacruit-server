from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.recruiting.services import RecruitingService
from wacruit.src.apps.user.models import User


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


def test_get_recruiting_by_id(
    recruiting_service: RecruitingService, recruiting: Recruiting, user: User
):
    recruiting_response = recruiting_service.get_recruiting_by_id(recruiting.id, user)
    assert recruiting_response.name == recruiting.name
    assert recruiting_response.is_active == recruiting.is_active
    assert recruiting_response.from_date == recruiting.from_date
    assert recruiting_response.to_date == recruiting.to_date
    assert recruiting_response.description == recruiting.description

    problems = recruiting_response.problem_status
    assert len(problems) == 1
