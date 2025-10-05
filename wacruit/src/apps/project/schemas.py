from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from wacruit.src.apps.common.enums import ProjectType
from wacruit.src.apps.common.enums import ProjectURLType
from wacruit.src.apps.common.schemas import OrmModel


class ProjectLinkDto(BaseModel):
    url_type: ProjectURLType
    url: str


class PresignedUrlWithIdResponse(BaseModel):
    object_name: str
    presigned_url: str
    fields: dict[str, str] = Field(default={})
    project_image_id: int


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., max_length=30)
    summary: str | None = Field(None, max_length=50)
    introduction: str | None = Field(None, max_length=255)
    project_type: ProjectType
    formed_at: datetime | None
    is_active: bool
    urls: list[ProjectLinkDto] | None


class ProjectUpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=30)
    summary: str | None = Field(None, max_length=50)
    introduction: str | None = Field(None, max_length=255)
    project_type: ProjectType | None
    formed_at: datetime | None
    is_active: bool | None
    urls: list[ProjectLinkDto] | None


class ProjectImageResponse(OrmModel):
    id: int
    project_id: int
    object_key: str
    is_uploaded: bool


class ProjectDetailResponse(OrmModel):
    id: int
    name: str
    summary: str | None
    introduction: str | None
    thumbnail_image: PresignedUrlWithIdResponse | None
    project_type: ProjectType
    formed_at: datetime | None
    is_active: bool
    images: list[PresignedUrlWithIdResponse] | None
    urls: list[ProjectLinkDto] | None


class ProjectBriefResponse(OrmModel):
    id: int
    name: str
    summary: str | None
    thumbnail_url: str | None
    project_type: ProjectType
    is_active: bool
    formed_at: datetime | None

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            name=obj.name,
            summary=obj.summary,
            thumbnail_url=obj.thumbnail_url,
            project_type=obj.project_type.name,
            is_active=obj.is_active,
            formed_at=obj.formed_at,
        )


class ProjectImageUploadRequest(BaseModel):
    project_id: int
    file_name: str


class ProjectListResponse(OrmModel):
    projects: list[ProjectBriefResponse]
