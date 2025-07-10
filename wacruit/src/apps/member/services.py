from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.member.exceptions import MemberAlreadyExistsException
from wacruit.src.apps.member.exceptions import MemberNotFoundException
from wacruit.src.apps.member.models import Member
from wacruit.src.apps.member.repositories import MemberRepository
from wacruit.src.apps.member.schemas import MemberBriefResponse
from wacruit.src.apps.member.schemas import MemberCreateRequest
from wacruit.src.apps.member.schemas import MemberInfoResponse
from wacruit.src.apps.member.schemas import MemberUpdateRequest
from wacruit.src.apps.user.repositories import UserRepository


class MemberService:
    def __init__(
        self,
        user_repository: UserRepository = Depends(),
        member_repository: MemberRepository = Depends(),
    ):
        self.user_repository = user_repository
        self.member_repository = member_repository

    def create_member(self, request: MemberCreateRequest):
        member = Member(
            first_name=request.first_name,
            last_name=request.last_name,
            introduction=request.introduction,
            department=request.department,
            college=request.college,
            phone_number=request.phone_number,
            github_id=request.github_id,
            is_active=request.is_active,
            generation=request.generation,
            position=request.position,
        )
        try:
            member = self.member_repository.create_member(member)
        except IntegrityError as exc:
            raise MemberAlreadyExistsException() from exc
        return MemberInfoResponse.from_orm(member)

    def get_member_by_id(self, member_id: int) -> MemberInfoResponse:
        member = self.member_repository.get_member_by_id(member_id)
        if member is None:
            raise MemberNotFoundException
        return MemberInfoResponse.from_orm(member)

    def get_members(
        self, waffle_sso_id: str | None
    ) -> ListResponse[MemberBriefResponse] | ListResponse[MemberInfoResponse]:
        members = self.member_repository.get_all_members()
        if waffle_sso_id:
            user = self.user_repository.get_user_by_sso_id(waffle_sso_id)
            if user and user.is_admin:
                return ListResponse[MemberInfoResponse](
                    items=[MemberInfoResponse.from_orm(member) for member in members]
                )
        return ListResponse[MemberBriefResponse](
            items=[MemberBriefResponse.from_orm(member) for member in members]
        )

    def update_member(
        self, member_id: int, request: MemberUpdateRequest
    ) -> MemberInfoResponse:
        member = self.member_repository.get_member_by_id(member_id)
        if member is None:
            raise MemberNotFoundException

        for field, value in request.dict(exclude_unset=True).items():
            setattr(member, field, value)

        try:
            member = self.member_repository.update_member(member)
        except IntegrityError as exc:
            raise MemberAlreadyExistsException() from exc

        return MemberInfoResponse.from_orm(member)
