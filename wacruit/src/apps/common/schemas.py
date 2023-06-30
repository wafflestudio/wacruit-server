from typing import Generic, TypeVar

from pydantic.generics import GenericModel

T = TypeVar("T")


class ListResponse(GenericModel, Generic[T]):
    items: list[T]


class PaginatedResponse(GenericModel, Generic[T]):
    items: list[T]
    next_cursor: int | None = None
