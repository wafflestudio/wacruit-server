import pytest

from wacruit.src.apps.announcement.exceptions import AnnouncementNotFound
from wacruit.src.apps.announcement.services import AnnouncementService


def test_create_announcement(
    announcement_service: AnnouncementService, announcement_create_dto
):
    response = announcement_service.create_announcement(announcement_create_dto.copy())
    assert response.id is not None
    assert response.title == announcement_create_dto.title
    assert response.content == announcement_create_dto.content
    assert response.created_at is not None
    assert response.updated_at is not None


def test_list_announcements(
    announcement_service: AnnouncementService, announcement_create_dto
):
    announcement_service.create_announcement(announcement_create_dto)
    announcement_service.create_announcement(announcement_create_dto)
    announcements = announcement_service.list_announcements()
    assert len(announcements) == 2


def test_list_pinned_announcements(
    announcement_service: AnnouncementService,
    announcement_create_dto,
    pinned_announcement_create_dto,
):
    announcement_service.create_announcement(announcement_create_dto)
    announcement_service.create_announcement(announcement_create_dto)
    announcement_service.create_announcement(pinned_announcement_create_dto)
    announcements = announcement_service.list_pinned_announcements()
    assert len(announcements) == 1
    assert announcements[0].pinned is True


def test_update_announcement(
    announcement_service: AnnouncementService,
    announcement_create_dto,
    announcement_update_dto,
):
    response = announcement_service.create_announcement(announcement_create_dto.copy())
    assert response.id is not None
    updated_announcement = announcement_service.update_announcement(
        response.id, announcement_update_dto.copy()
    )
    assert updated_announcement.title == announcement_update_dto.title
    assert updated_announcement.content == announcement_update_dto.content
    assert updated_announcement.pinned == announcement_update_dto.pinned


def test_update_announcement_with_updated_at(
    announcement_service: AnnouncementService,
    announcement_create_dto,
    announcement_update_dto,
):
    response = announcement_service.create_announcement(announcement_create_dto.copy())
    assert response.id is not None
    created_announcement = announcement_service.get_announcement(response.id)
    updated_announcement = announcement_service.update_announcement(
        response.id, announcement_update_dto.copy()
    )
    assert updated_announcement.created_at == created_announcement.created_at
    assert updated_announcement.updated_at >= created_announcement.updated_at


def test_update_announcement_not_found(
    announcement_service: AnnouncementService, announcement_update_dto
):
    with pytest.raises(AnnouncementNotFound):
        announcement_service.update_announcement(
            999, announcement_update_dto
        )  # Assumption that ID 999 does not exist.


def test_delete_announcement(
    announcement_service: AnnouncementService, announcement_create_dto
):
    response = announcement_service.create_announcement(announcement_create_dto.copy())
    assert response.id is not None
    announcement_service.delete_announcement(response.id)
    with pytest.raises(AnnouncementNotFound):
        announcement_service.get_announcement(response.id)


def test_delete_announcement_twice(
    announcement_service: AnnouncementService, announcement_create_dto
):
    response = announcement_service.create_announcement(announcement_create_dto.copy())
    assert response.id is not None
    announcement_service.delete_announcement(response.id)
    announcement_service.delete_announcement(response.id)
