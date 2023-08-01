from functools import cache
from textwrap import shorten
from typing import Any, Callable

from sqlalchemy import Column
from sqlalchemy.orm import DeclarativeBase

Formatter = Callable[[type[DeclarativeBase], Column[Any]], str | None]


def recruiting_formatter(
    model: type[DeclarativeBase], attribute: Column[Any]
) -> str | None:
    recruiting = getattr(model, "recruiting")
    return recruiting and recruiting.name


def user_formatter(model: type[DeclarativeBase], attribute: Column[Any]) -> str | None:
    user = getattr(model, "user")
    return user and f"{user.last_name} {user.first_name}"


@cache
def shorten_column(width: int = 10, placeholder: str = "...", **kwargs) -> Formatter:
    def formatter(model: type[DeclarativeBase], attribute: Column[Any]):
        column = getattr(model, attribute.key)
        return column and shorten(
            str(column), width=width, placeholder=placeholder, **kwargs
        )

    return formatter
