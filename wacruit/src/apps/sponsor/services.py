from typing import Annotated

from fastapi import Depends

from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.sponsor.exceptions import SponsorAlreadyExistsException
from wacruit.src.apps.sponsor.exceptions import SponsorNotFoundException
from wacruit.src.apps.sponsor.models import Sponsor
from wacruit.src.apps.sponsor.repositories import SponsorRepository
from wacruit.src.apps.sponsor.schemas import SponsorBriefResponse
from wacruit.src.apps.sponsor.schemas import SponsorCreateRequest
from wacruit.src.apps.sponsor.schemas import SponsorInfoResponse
from wacruit.src.apps.sponsor.schemas import SponsorUpdateRequest


class SponsorService:
    def __init__(self, sponsor_repository: Annotated[SponsorRepository, Depends()]):
        self.sponsor_repository = sponsor_repository

    def create_sponsor(self, request: SponsorCreateRequest):
        if self.sponsor_repository.get_sponsor_by_sponsor_name(request.name):
            raise SponsorAlreadyExistsException
        sponsor = Sponsor(
            name=request.name,
            amount=request.amount,
            email=request.email,
            phone_number=request.phone_number,
            sponsored_date=request.sponsored_date,
        )
        return self.sponsor_repository.create_sponsor(sponsor)

    def get_sponsor_by_id(self, sponsor_id: str) -> SponsorInfoResponse:
        sponsor = self.sponsor_repository.get_sponsor_by_id(sponsor_id)
        if not sponsor:
            raise SponsorNotFoundException
        return SponsorInfoResponse.from_orm(sponsor)

    def get_all_sponsors(self) -> ListResponse[SponsorBriefResponse]:
        sponsors = self.sponsor_repository.get_all_sponsors()
        return (
            ListResponse[SponsorBriefResponse](
                items=[SponsorBriefResponse.from_orm(sponsor) for sponsor in sponsors]
            )
            if sponsors
            else ListResponse[SponsorBriefResponse](items=[])
        )

    def update_sponsor(
        self, sponsor_id: str, request: SponsorUpdateRequest
    ) -> SponsorInfoResponse:
        sponsor = self.sponsor_repository.get_sponsor_by_id(sponsor_id)
        if not sponsor:
            raise SponsorNotFoundException

        for field, value in request.dict(exclude_none=True).items():
            setattr(sponsor, field, value)

        self.sponsor_repository.update_sponsor(sponsor)

        return SponsorInfoResponse.from_orm(sponsor)
