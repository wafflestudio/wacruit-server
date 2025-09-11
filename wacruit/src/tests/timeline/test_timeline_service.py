from datetime import datetime
from typing import List

import pytest

from wacruit.src.apps.timeline.exceptions import TimelineCategoryNotFoundException
from wacruit.src.apps.timeline.exceptions import TimelineNotFoundException
from wacruit.src.apps.timeline.models import Timeline
from wacruit.src.apps.timeline.models import TimelineCategory
from wacruit.src.apps.timeline.schemas import TimelineGroupType
from wacruit.src.apps.timeline.services import TimelineService


def test_create_category(timeline_service: TimelineService, category_create_dto):
    response = timeline_service.create_category(category_create_dto)

    assert response.title == "친목"


def test_update_category(
    timeline_service: TimelineService,
    timeline_category1: TimelineCategory,
    category_update_dto,
):
    response = timeline_service.update_category(
        timeline_category1.id, category_update_dto
    )

    assert response.title == "세미나"


def test_get_all_categories(
    timeline_service: TimelineService, created_category_list: List[TimelineCategory]
):
    response = timeline_service.get_all_categories()
    category_list = response.items

    assert len(created_category_list) == len(category_list)
    for i in range(0, 5):
        assert category_list[i].title == f"카테고리 {i}"


def test_delete_category(timeline_service: TimelineService, timeline_category1):
    created_id = timeline_category1.id
    timeline_service.delete_category(created_id)
    with pytest.raises(TimelineCategoryNotFoundException):
        timeline_service.delete_category(created_id)


def test_create_timeline(timeline_service: TimelineService, timeline_create_dto):
    response = timeline_service.create_timeline(timeline_create_dto)

    assert response.title == "New Timeline"
    assert response.group == TimelineGroupType.ROOKIE
    assert response.category.title == "친목"
    assert response.start_date == datetime(2025, 1, 1)
    assert response.end_date == datetime(2025, 1, 5)


def test_update_timeline(
    timeline_service: TimelineService, created_timeline: Timeline, timeline_update_dto
):
    response = timeline_service.update_timeline(
        created_timeline.id, timeline_update_dto
    )

    assert response.title == "Updated Timeline"
    assert response.group == TimelineGroupType.PROGRAMMER
    assert response.category.title == "세미나"
    assert response.start_date == datetime(2025, 3, 1)
    assert response.end_date == datetime(2025, 3, 5)


def test_get_all_timelines(
    timeline_service: TimelineService, created_timeline_list: List[Timeline]
):
    response = timeline_service.get_all_timelines(TimelineGroupType.ROOKIE)
    timeline_list = response.items

    assert len(timeline_list) == len(created_timeline_list)
    for i in range(0, 5):
        assert timeline_list[i].title == f"Created Timeline {i}"
        assert timeline_list[i].group == TimelineGroupType.ROOKIE
        assert timeline_list[i].category.title == "친목"
        assert timeline_list[i].start_date == datetime(2025, 1, 1)
        assert timeline_list[i].end_date == datetime(2025, 1, 5)


def test_delete_timeline_success(
    timeline_service: TimelineService, created_timeline: Timeline
):
    created_id = created_timeline.id
    timeline_service.delete_timeline(created_id)
    with pytest.raises(TimelineNotFoundException):
        timeline_service.get_timeline_by_id(created_id)


def test_delete_timeline_not_found(timeline_service: TimelineService):
    with pytest.raises(TimelineNotFoundException):
        timeline_service.delete_timeline(999)
