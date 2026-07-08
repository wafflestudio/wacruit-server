from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy.orm import Session

from wacruit.src.apps.common.enums import TimelineGroupType
from wacruit.src.apps.timeline.models import Timeline
from wacruit.src.apps.timeline.models import TimelineCategory
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


class TimelineRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    def create_category(self, category: TimelineCategory) -> TimelineCategory:
        with self.transaction:
            self.session.add(category)
        return category

    def get_all_categories(
        self, group: TimelineGroupType | None = None
    ) -> list[TimelineCategory]:
        if group is None:
            return self.session.query(TimelineCategory).all()

        return (
            self.session.query(TimelineCategory)
            .join(Timeline, TimelineCategory.id == Timeline.category_id)
            .filter(Timeline.group == group)
            .distinct()
            .all()
        )

    def get_category_by_id(self, category_id: int) -> TimelineCategory | None:
        return self.session.query(TimelineCategory).filter_by(id=category_id).first()

    def update_category(self, category: TimelineCategory) -> TimelineCategory:
        with self.transaction:
            self.session.merge(category)
        return category

    def delete_category(self, category: TimelineCategory):
        with self.transaction:
            self.session.delete(category)
        return category

    def create_timeline(self, timeline: Timeline) -> Timeline:
        with self.transaction:
            self.session.add(timeline)
        return timeline

    def get_timeline_by_id(self, timeline_id: int) -> Timeline | None:
        return self.session.query(Timeline).filter_by(id=timeline_id).first()

    def get_all_timelines(
        self, group: TimelineGroupType | None = None
    ) -> list[Timeline]:
        if group is None:
            return self.session.query(Timeline).all()

        return self.session.query(Timeline).filter(Timeline.group == group).all()

    def update_timeline(self, timeline: Timeline) -> Timeline:
        with self.transaction:
            self.session.merge(timeline)
        return timeline

    def delete_timeline(self, timeline_id: int):
        with self.transaction:
            self.session.execute(delete(Timeline).where(Timeline.id == timeline_id))
