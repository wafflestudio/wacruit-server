from functools import cache
from textwrap import shorten
from typing import Callable

from sqlalchemy.orm import DeclarativeBase

Formatter = Callable[[type[DeclarativeBase], str], str | None]


def recruiting_formatter(model: type[DeclarativeBase], attribute: str) -> str | None:
    recruiting = getattr(model, "recruiting")
    return recruiting and recruiting.name


def user_formatter(model: type[DeclarativeBase], attribute: str) -> str | None:
    user = getattr(model, "user")
    return user and f"{user.last_name} {user.first_name}"


@cache
def shorten_column(width: int = 10, placeholder: str = "...", **kwargs) -> Formatter:
    def formatter(model: type[DeclarativeBase], attribute: str):
        column = getattr(model, attribute)
        return column and shorten(
            str(column), width=width, placeholder=placeholder, **kwargs
        )

    return formatter


def member_formatter(model: type[DeclarativeBase], attribute: str) -> str | None:
    member = getattr(model, "member")
    return member and f"{member.last_name} {member.first_name}"


def timeline_category_formatter(
    model: type[DeclarativeBase], attribute: str
) -> str | None:
    category = getattr(model, "category")
    return category and category.title


def project_urls_formatter(model: type[DeclarativeBase], attribute: str):
    urls = getattr(model, "urls", None) or []
    return [
        getattr(getattr(u, "url_type", None), "name", str(getattr(u, "url_type", "")))
        for u in urls
    ]
