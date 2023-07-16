from typing import Any, Generic, Sequence, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class ListResponse(GenericModel, Generic[T]):
    items: list[T]


class PaginatedResponse(GenericModel, Generic[T]):
    items: list[T]
    next_cursor: int | None = None


class OrmModel(BaseModel):
    @classmethod
    def from_orm_sequence(cls, seq: Sequence[Any]):
        return list(map(cls.from_orm, seq))

    class Config:
        orm_mode = True
