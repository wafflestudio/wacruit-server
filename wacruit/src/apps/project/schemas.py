from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from wacruit.src.apps.common.enums import ProjectType
from wacruit.src.apps.common.schemas import OrmModel


class ProjectLinkDto(BaseModel):
    title: str
    url: str


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., max_length=30)
    summary: str | None = Field(None, max_length=50)
    introduction: str | None = Field(None, max_length=255)
    thumbnail_url: str | None = Field(None, max_length=255)
    leader_id: int
    project_type: str
    is_active: bool
    images: list[str] | None
    urls: list[ProjectLinkDto] | None


class ProjectUpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=30)
    summary: str | None = Field(None, max_length=50)
    introduction: str | None = Field(None, max_length=255)
    thumbnail_url: str | None = Field(None, max_length=255)
    project_type: str | None
    is_active: bool | None
    images: list[str] | None
    urls: list[ProjectLinkDto] | None


class ProjectDetailResponse(OrmModel):
    id: int
    name: str
    summary: str | None
    introduction: str | None
    thumbnail_url: str | None
    leader_id: int
    project_type: str  # enum 문자열로 변경
    is_active: bool
    images: list[str] | None
    urls: list[ProjectLinkDto] | None

    @classmethod
    def from_orm(cls, obj):
        urls = None
        if obj.urls:
            urls = [ProjectLinkDto(title=url.title, url=url.url) for url in obj.urls]

        images = None
        if obj.image_urls:
            images = [img.url for img in obj.image_urls]

        return cls(
            id=obj.id,
            name=obj.name,
            summary=obj.summary,
            introduction=obj.introduction,
            thumbnail_url=obj.thumbnail_url,
            leader_id=obj.leader_id,
            project_type=obj.project_type.name,
            is_active=obj.is_active,
            images=images,
            urls=urls,
        )


class ProjectBriefResponse(OrmModel):
    id: int
    name: str
    summary: str | None
    thumbnail_url: str | None
    project_type: str
    is_active: bool

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            name=obj.name,
            summary=obj.summary,
            thumbnail_url=obj.thumbnail_url,
            project_type=obj.project_type.name,
            is_active=obj.is_active,
        )


class ProjectListResponse(OrmModel):
    projects: list[ProjectBriefResponse]


class ProjectMemberCreateRequest(BaseModel):
    member_id: int
    name: str
    position: str


class ProjectMemberResponse(OrmModel):
    member_id: int
    member_name: str
    position: str


class ProjectMemberListResponse(OrmModel):
    members: list[ProjectMemberResponse]


class ProjectMemberUpdateRequest(BaseModel):
    name: str | None
    position: str | None
