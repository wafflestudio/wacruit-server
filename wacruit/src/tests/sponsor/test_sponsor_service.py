from typing import List

import pytest

from wacruit.src.apps.sponsor.exceptions import SponsorAlreadyExistsException
from wacruit.src.apps.sponsor.exceptions import SponsorNotFoundException
from wacruit.src.apps.sponsor.models import Sponsor
from wacruit.src.apps.sponsor.schemas import SponsorCreateRequest
from wacruit.src.apps.sponsor.schemas import SponsorUpdateRequest
from wacruit.src.apps.sponsor.services import SponsorService


def test_create_sponsor(
    sponsor_service: SponsorService, sponsor_create_dto: SponsorCreateRequest
):
    created_sponsor = sponsor_service.create_sponsor(sponsor_create_dto)

    assert created_sponsor.id is not None
    assert created_sponsor.name == sponsor_create_dto.name
    assert created_sponsor.email == sponsor_create_dto.email
    assert created_sponsor.phone_number == sponsor_create_dto.phone_number
    assert created_sponsor.sponsored_date == sponsor_create_dto.sponsored_date


def test_create_duplicate_sponsor(
    sponsor_service: SponsorService, sponsor_create_dto: SponsorCreateRequest
):
    sponsor_service.create_sponsor(sponsor_create_dto)
    with pytest.raises(SponsorAlreadyExistsException):
        sponsor_service.create_sponsor(sponsor_create_dto)


def test_get_sponsor_by_existing_id(
    sponsor_service: SponsorService, created_sponsor: Sponsor
):
    sponsor = sponsor_service.get_sponsor_by_id(created_sponsor.id)
    assert sponsor.id == created_sponsor.id
    assert sponsor.name == created_sponsor.name
    assert sponsor.amount == created_sponsor.amount
    assert sponsor.email == created_sponsor.email
    assert sponsor.phone_number == created_sponsor.phone_number
    assert sponsor.sponsored_date == created_sponsor.sponsored_date


def test_get_sponsor_by_non_existing_id(sponsor_service: SponsorService):
    with pytest.raises(SponsorNotFoundException):
        sponsor_service.get_sponsor_by_id(1234)


def test_get_all_sponsors(
    sponsor_service: SponsorService, created_sponsor_list: List[Sponsor]
):
    sponsors = sponsor_service.get_all_sponsors()
    assert len(sponsors.items) == len(created_sponsor_list)
    for i in range(3):
        assert sponsors.items[i].name == created_sponsor_list[i].name


def test_update_sponsor(
    sponsor_service: SponsorService,
    sponsor_create_dto: SponsorCreateRequest,
    sponsor_update_dto: SponsorUpdateRequest,
):
    sponsor = sponsor_service.create_sponsor(sponsor_create_dto)
    assert sponsor.id is not None
    updated_sponsor = sponsor_service.update_sponsor(sponsor.id, sponsor_update_dto)
    assert updated_sponsor.amount == sponsor_update_dto.amount
    assert updated_sponsor.email == sponsor_update_dto.email
    assert updated_sponsor.phone_number == sponsor_update_dto.phone_number
