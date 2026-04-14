from datetime import datetime
from urllib.parse import urlparse

from botocore.exceptions import ClientError
import pytest

from wacruit.src.apps.common.enums import ProjectType
from wacruit.src.apps.portfolio.file.aws.config import storage_config
from wacruit.src.apps.project.models import Project
from wacruit.src.apps.project.repositories import ProjectRepository
from wacruit.src.apps.project.schemas import ProjectImageResponse
from wacruit.src.apps.project.services import ProjectService
from wacruit.src.database.connection import Transaction


@pytest.fixture
def project_repository(db_session):
    return ProjectRepository(session=db_session, transaction=Transaction(db_session))


@pytest.fixture
def project_service(project_repository: ProjectRepository):
    return ProjectService(project_repository=project_repository)


@pytest.fixture
def project(db_session):
    project = Project(
        name="ProjectSmoke",
        summary="summary",
        introduction="introduction",
        project_type=ProjectType.SERVICE,
        formed_at=datetime.utcnow(),
        is_active=True,
    )
    db_session.add(project)
    db_session.commit()
    return project


def test_get_upload_project_image_url(
    project: Project,
    project_service: ProjectService,
):
    response = project_service.generate_presigned_url_for_post_image(
        project_id=project.id,
        file_name="image.png",
    )
    expected_object_name = f"PROJECT/{project.id}/image.png"
    expected_url = (
        f"{storage_config.endpoint_url}/{storage_config.bucket_name}"
        if storage_config.endpoint_url
        else f"https://{storage_config.bucket_name}.s3.amazonaws.com/"
    )

    assert response.object_name == expected_object_name
    assert response.project_image_id > 0
    assert response.presigned_url == expected_url
    assert response.fields["key"] == expected_object_name
    assert response.fields["x-amz-algorithm"] == "AWS4-HMAC-SHA256"
    assert response.fields["x-amz-credential"].endswith(
        f"/{storage_config.region}/s3/aws4_request"
    )
    assert response.fields["Cache-Control"] == "max-age=7889400"
    assert "x-amz-date" in response.fields
    assert "policy" in response.fields
    assert "x-amz-signature" in response.fields


def test_register_and_get_download_project_image_url(
    project: Project,
    project_service: ProjectService,
):
    upload_response = project_service.generate_presigned_url_for_post_image(
        project_id=project.id,
        file_name="image.png",
    )
    register_response = project_service.register_project_image_info_in_db(
        file_id=upload_response.project_image_id
    )

    assert register_response == ProjectImageResponse(
        id=upload_response.project_image_id,
        project_id=project.id,
        object_key=f"PROJECT/{project.id}/image.png",
        is_uploaded=True,
    )

    presigned_url = project_service.generate_presigned_url_for_get_image(
        upload_response.project_image_id
    )
    url, _ = presigned_url.split("?")
    parsed = urlparse(url)
    expected_path = f"/{storage_config.bucket_name}/PROJECT/{project.id}/image.png"

    if storage_config.endpoint_url:
        endpoint = urlparse(storage_config.endpoint_url)
        assert parsed.scheme == endpoint.scheme
        assert parsed.netloc == endpoint.netloc
        assert parsed.path == expected_path
    else:
        assert url == (
            f"https://{storage_config.bucket_name}.s3.amazonaws.com/"
            f"PROJECT/{project.id}/image.png"
        )


def test_delete_project_image(
    project: Project,
    project_service: ProjectService,
):
    upload_response = project_service.generate_presigned_url_for_post_image(
        project_id=project.id,
        file_name="image.png",
    )
    project_service.register_project_image_info_in_db(
        file_id=upload_response.project_image_id
    )

    project_service.delete_project_image(upload_response.project_image_id)

    with pytest.raises(ClientError):
        project_service._s3_client.client.head_object(
            Bucket=storage_config.bucket_name,
            Key=f"PROJECT/{project.id}/image.png",
        )

    assert (
        project_service.project_repository.get_project_image_by_id(
            upload_response.project_image_id
        )
        is None
    )
