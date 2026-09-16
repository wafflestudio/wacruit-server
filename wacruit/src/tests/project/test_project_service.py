from datetime import datetime
from unittest.mock import MagicMock

from wacruit.src.apps.common.enums import ProjectType
from wacruit.src.apps.project.models import Project
from wacruit.src.apps.project.models import ProjectImage
from wacruit.src.apps.project.services import ProjectService


def create_project(*images: ProjectImage) -> Project:
    project = Project(
        id=1,
        name="project",
        summary="summary",
        introduction="introduction",
        project_type=ProjectType.SERVICE,
        formed_at=datetime(2025, 1, 1),
        is_active=True,
    )
    project.images = list(images)
    project.urls = []
    return project


def create_service(
    project_repository: MagicMock,
) -> tuple[ProjectService, MagicMock]:
    service = object.__new__(ProjectService)
    service.project_repository = project_repository
    generate_presigned_url = MagicMock(return_value="presigned-url")
    service._generate_presigned_url_for_get_object = generate_presigned_url
    return service, generate_presigned_url


def test_get_project_uses_loaded_image_without_querying_it_again():
    image = ProjectImage(
        id=1,
        project_id=1,
        object_key="PROJECT/1/image.png",
        is_uploaded=True,
        is_thumbnail=False,
    )
    project_repository = MagicMock()
    project_repository.get_project_by_id.return_value = create_project(image)
    service, generate_presigned_url = create_service(project_repository)

    response = service.get_project(project_id=1)

    project_repository.get_project_image_by_id.assert_not_called()
    generate_presigned_url.assert_called_once_with(image.object_key)
    assert response.images is not None
    assert response.images[0].project_image_id == image.id


def test_list_projects_uses_loaded_thumbnail_without_querying_it_again():
    thumbnail = ProjectImage(
        id=1,
        project_id=1,
        object_key="PROJECT/1/thumbnail/image.png",
        is_uploaded=True,
        is_thumbnail=True,
    )
    project_repository = MagicMock()
    project_repository.get_projects.return_value = [create_project()]
    project_repository.get_thumbnail_image_by_project_id.return_value = thumbnail
    service, generate_presigned_url = create_service(project_repository)

    response = service.list_projects()

    project_repository.get_project_image_by_id.assert_not_called()
    generate_presigned_url.assert_called_once_with(thumbnail.object_key)
    assert response.items[0].thumbnail_image is not None
    assert response.items[0].thumbnail_image.project_image_id == thumbnail.id
