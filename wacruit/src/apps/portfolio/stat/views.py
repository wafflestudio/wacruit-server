from http import HTTPStatus
from typing import Annotated

import fastapi

from wacruit.src.apps.portfolio.file.services import PortfolioFileService
from wacruit.src.apps.portfolio.stat.schemas import NumOfAllApplicants
from wacruit.src.apps.portfolio.url.services import PortfolioUrlService

v1_router = fastapi.APIRouter(prefix="/stat", tags=["portfolio-stat"])


@v1_router.get(
    path="",
    status_code=HTTPStatus.OK,
)
def get_num_of_applicants(
    file_service: Annotated[PortfolioFileService, fastapi.Depends()],
    url_service: Annotated[PortfolioUrlService, fastapi.Depends()],
) -> NumOfAllApplicants:
    file_applicant_user_ids = file_service.get_all_applicant_user_ids()
    url_applicant_user_ids = url_service.get_all_applicant_user_ids()
    num_of_all_applicants = len(set(file_applicant_user_ids + url_applicant_user_ids))
    return NumOfAllApplicants(num=num_of_all_applicants)
