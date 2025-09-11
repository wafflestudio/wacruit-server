from typing import List

import pytest

from wacruit.src.apps.seminar.models import Seminar
from wacruit.src.apps.seminar.models import SeminarType
from wacruit.src.apps.seminar.schemas import CreateSeminarRequest
from wacruit.src.apps.seminar.schemas import UpdateSeminarRequest
from wacruit.src.apps.seminar.services import SeminarService


def test_create_seminar(
    create_seminar_dto: CreateSeminarRequest, seminar_service: SeminarService
):
    res = seminar_service.create_seminar(create_seminar_dto)

    assert res.seminar_type == create_seminar_dto.seminar_type
    assert res.curriculum_info == create_seminar_dto.curriculum_info
    assert res.prerequisite_info == create_seminar_dto.prerequisite_info
    assert res.is_active == create_seminar_dto.is_active


def test_get_active_seminar(
    created_active_seminar: Seminar,
    created_not_active_seminar: Seminar,
    seminar_service: SeminarService,
):
    res = seminar_service.get_active_seminar()

    assert len(res) == 1
    assert res[0].id == created_active_seminar.id
    assert res[0].seminar_type == created_active_seminar.seminar_type
    assert res[0].curriculum_info == created_active_seminar.curriculum_info
    assert res[0].prerequisite_info == created_active_seminar.prerequisite_info
    assert res[0].is_active == created_active_seminar.is_active


def test_get_all_seminars(
    created_seminars: List[Seminar], seminar_service: SeminarService
):
    created_size = len(created_seminars)
    res = seminar_service.get_all_seminars()

    assert len(res) == created_size

    for i in range(created_size):
        assert res[i].id == created_seminars[i].id
        assert res[i].seminar_type == created_seminars[i].seminar_type
        assert res[i].curriculum_info == created_seminars[i].curriculum_info
        assert res[i].prerequisite_info == created_seminars[i].prerequisite_info
        assert res[i].is_active == created_seminars[i].is_active


def test_get_seminar_by_id(
    seminar_service: SeminarService, created_active_seminar: Seminar
):
    created_id = created_active_seminar.id
    res = seminar_service.get_seminar_by_id(created_id)

    assert res.id == created_id
    assert res.seminar_type == created_active_seminar.seminar_type
    assert res.curriculum_info == created_active_seminar.curriculum_info
    assert res.prerequisite_info == created_active_seminar.prerequisite_info
    assert res.is_active == created_active_seminar.is_active


def test_update_seminar(
    seminar_service: SeminarService,
    created_active_seminar: Seminar,
    update_seminar_dto: UpdateSeminarRequest,
):
    created_id = created_active_seminar.id
    res = seminar_service.update_seminar(created_id, update_seminar_dto)

    assert res.seminar_type == update_seminar_dto.seminar_type
    assert res.curriculum_info == update_seminar_dto.curriculum_info
    assert res.prerequisite_info == update_seminar_dto.prerequisite_info
    assert res.is_active == update_seminar_dto.is_active
