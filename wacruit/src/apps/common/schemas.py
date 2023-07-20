from typing import Any, Generic, Iterable, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")
Model = TypeVar("Model", bound="BaseModel")


class ListResponse(GenericModel, Generic[T]):
    items: list[T]


class PaginatedResponse(GenericModel, Generic[T]):
    items: list[T]
    next_cursor: int | None = None


class OrmModel(BaseModel):
    @classmethod
    def from_orm_all(cls: type[Model], objs: Iterable[Any]) -> list[Model]:
        return list(map(cls.from_orm, objs))

    class Config:
        orm_mode = True
