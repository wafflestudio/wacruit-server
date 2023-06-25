from fastapi import Depends

from wacruit.src.apps.announcement.exceptions import AnnouncementNotFound
from wacruit.src.apps.announcement.models import Announcement
from wacruit.src.apps.announcement.repositories import AnnouncementRepository
from wacruit.src.apps.announcement.schemas import AnnouncementCreateDto
from wacruit.src.apps.announcement.schemas import AnnouncementDto


class AnnouncementService:
    def __init__(
        self, announcement_repository: AnnouncementRepository = Depends()
    ) -> None:
        self.announcement_repository = announcement_repository

    def create_announcement(self, request: AnnouncementCreateDto) -> AnnouncementDto:
        announcement = Announcement(title=request.title, content=request.content)
        announcement = self.announcement_repository.create_announcement(announcement)
        return AnnouncementDto.from_orm(announcement)

    def list_announcements(self) -> list[AnnouncementDto]:
        announcements = self.announcement_repository.get_announcements()
        return [
            AnnouncementDto.from_orm(announcement) for announcement in announcements
        ]

    def update_announcement(
        self, id: int, request: AnnouncementCreateDto
    ) -> AnnouncementDto:
        announcement = self.announcement_repository.get_announcement(id)
        if announcement is None:
            raise AnnouncementNotFound
        announcement.title = request.title
        announcement.content = request.content
        announcement = self.announcement_repository.update_announcement(announcement)
        return AnnouncementDto.from_orm(announcement)

    def get_announcement(self, id: int) -> AnnouncementDto:
        announcement = self.announcement_repository.get_announcement(id)
        if announcement is None:
            raise AnnouncementNotFound
        return AnnouncementDto.from_orm(announcement)
