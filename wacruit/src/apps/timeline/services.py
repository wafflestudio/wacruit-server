from typing import Annotated

from fastapi import Depends

from wacruit.src.apps.common.enums import TimelineGroupType
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.timeline.exceptions import TimelineCategoryNotFoundException
from wacruit.src.apps.timeline.exceptions import TimelineNotFoundException
from wacruit.src.apps.timeline.models import Timeline
from wacruit.src.apps.timeline.models import TimelineCategory
from wacruit.src.apps.timeline.repositories import TimelineRepository
from wacruit.src.apps.timeline.schemas import TimelineCategoryCreateUpdateRequest
from wacruit.src.apps.timeline.schemas import TimelineCategoryResponse
from wacruit.src.apps.timeline.schemas import TimelineCreateRequest
from wacruit.src.apps.timeline.schemas import TimelineResponse
from wacruit.src.apps.timeline.schemas import TimelineUpdateRequest


class TimelineService:
    def __init__(
        self,
        timeline_repository: TimelineRepository = Depends(),
    ):
        self.timeline_repository = timeline_repository

    def create_category(
        self, request: TimelineCategoryCreateUpdateRequest
    ) -> TimelineCategoryResponse:
        category = TimelineCategory(
            title=request.title,
        )
        created_category = self.timeline_repository.create_category(category)
        return TimelineCategoryResponse.from_orm(created_category)

    def get_all_categories(
        self, group: TimelineGroupType | None = None
    ) -> ListResponse[TimelineCategoryResponse]:
        categories = self.timeline_repository.get_all_categories(group=group)
        return (
            ListResponse(
                items=[
                    TimelineCategoryResponse.from_orm(category)
                    for category in categories
                ]
            )
            if categories
            else ListResponse(items=[])
        )

    def update_category(
        self, category_id: int, request: TimelineCategoryCreateUpdateRequest
    ) -> TimelineCategoryResponse:
        category = self.timeline_repository.get_category_by_id(category_id)
        if not category:
            raise TimelineCategoryNotFoundException
        category.title = request.title
        self.timeline_repository.update_category(category)
        return TimelineCategoryResponse.from_orm(category)

    def delete_category(self, category_id: int):
        category = self.timeline_repository.get_category_by_id(category_id)
        if not category:
            raise TimelineCategoryNotFoundException
        self.timeline_repository.delete_category(category)

    def create_timeline(self, request: TimelineCreateRequest) -> TimelineResponse:
        if not self.timeline_repository.get_category_by_id(request.category_id):
            raise TimelineCategoryNotFoundException
        timeline = Timeline(
            title=request.title,
            group=request.group,
            category_id=request.category_id,
            start_date=request.start_date,
            end_date=request.end_date,
        )
        created_timeline = self.timeline_repository.create_timeline(timeline)
        return TimelineResponse.from_orm(created_timeline)

    def get_timeline_by_id(self, timeline_id: int) -> TimelineResponse:
        timeline = self.timeline_repository.get_timeline_by_id(timeline_id)
        if not timeline:
            raise TimelineNotFoundException
        return TimelineResponse.from_orm(timeline)

    def get_all_timelines(
        self, group: TimelineGroupType | None = None
    ) -> ListResponse[TimelineResponse]:
        timelines = self.timeline_repository.get_all_timelines(group=group)
        return (
            ListResponse(
                items=[TimelineResponse.from_orm(timeline) for timeline in timelines]
            )
            if timelines
            else ListResponse(items=[])
        )

    def update_timeline(
        self, timeline_id: int, request: TimelineUpdateRequest
    ) -> TimelineResponse:
        timeline = self.timeline_repository.get_timeline_by_id(timeline_id)
        if not timeline:
            raise TimelineNotFoundException
        if request.category_id and not self.timeline_repository.get_category_by_id(
            request.category_id
        ):
            raise TimelineCategoryNotFoundException
        for key, value in request.dict(exclude_none=True).items():
            setattr(timeline, key, value)
        timeline = self.timeline_repository.update_timeline(timeline)
        return TimelineResponse.from_orm(timeline)

    def delete_timeline(self, timeline_id: int):
        if not self.timeline_repository.get_timeline_by_id(timeline_id):
            raise TimelineNotFoundException
        self.timeline_repository.delete_timeline(timeline_id)
