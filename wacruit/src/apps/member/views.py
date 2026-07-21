from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import Query
from fastapi import Security
from fastapi.security import APIKeyHeader

from wacruit.src.apps.common.enums import Position
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.common.security import verify_internal_bot
from wacruit.src.apps.member.schemas import DiscordMemberInfoResponse
from wacruit.src.apps.member.schemas import MemberBriefResponse
from wacruit.src.apps.member.schemas import MemberCreateRequest
from wacruit.src.apps.member.schemas import MemberInfoResponse
from wacruit.src.apps.member.schemas import MemberUpdateRequest
from wacruit.src.apps.member.services import MemberService
from wacruit.src.apps.user.dependencies import AdminUser
from wacruit.src.batch.discord.main import sync_discord_members

v3_router = APIRouter(prefix="/v3/members", tags=["members"])


@v3_router.post("", status_code=HTTPStatus.CREATED)
def create_member(
    admin_user: AdminUser,
    request: MemberCreateRequest,
    member_service: Annotated[MemberService, Depends()],
):
    member_service.create_member(request)


@v3_router.get("/discord")
def get_discord_members(
    member_service: Annotated[MemberService, Depends()],
    bot_token: Annotated[str, Depends(verify_internal_bot)],
) -> ListResponse[DiscordMemberInfoResponse]:
    return member_service.get_discord_member_info()


@v3_router.post("/discord/sync")
def trigger_discord_sync(
    background_tasks: BackgroundTasks,
    bot_token: Annotated[str, Depends(verify_internal_bot)],
):
    background_tasks.add_task(sync_discord_members)
    return {"message": "Discord member sync triggered in the background"}


@v3_router.get("/{member_id}")
def get_member(
    admin_user: AdminUser,
    member_id: int,
    member_service: Annotated[MemberService, Depends()],
) -> MemberInfoResponse:
    return member_service.get_member_by_id(member_id)


@v3_router.get("")
def get_members(
    waffle_sso_id: Annotated[
        str | None,
        Security(
            APIKeyHeader(
                name="waffle-user-id", scheme_name="waffle-user-id", auto_error=False
            )
        ),
    ],
    member_service: Annotated[MemberService, Depends()],
    position: Annotated[Position | None, Query()] = None,
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 20,
) -> ListResponse[MemberInfoResponse] | ListResponse[MemberBriefResponse]:
    return member_service.get_members(waffle_sso_id, position, offset, limit)


@v3_router.patch("/{member_id}")
def update_member(
    admin_user: AdminUser,
    member_id: int,
    request: MemberUpdateRequest,
    member_service: Annotated[MemberService, Depends()],
) -> MemberInfoResponse:
    return member_service.update_member(member_id, request)
