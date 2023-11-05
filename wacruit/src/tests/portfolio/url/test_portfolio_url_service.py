import pytest

from wacruit.src.apps.portfolio.url.exceptions import NumPortfolioUrlLimitException
from wacruit.src.apps.portfolio.url.exceptions import PortfolioUrlNotAuthorized
from wacruit.src.apps.portfolio.url.exceptions import PortfolioUrlNotFound
from wacruit.src.apps.portfolio.url.schemas import PortfolioUrlResponse
from wacruit.src.apps.portfolio.url.services import PortfolioUrlService
from wacruit.src.apps.user.models import User


def test_create_portfolio_url(
    created_user1: User,
    portfolio_url_service: PortfolioUrlService,
):
    response = portfolio_url_service.create_portfolio_url(
        user_id=created_user1.id,
        url="https://test1.com",
    )
    expected = PortfolioUrlResponse(
        id=1,
        url="https://test1.com",
    )
    assert response == expected

    portfolio_url_service.create_portfolio_url(
        user_id=created_user1.id,
        url="https://test2.com",
    )
    portfolio_url_service.create_portfolio_url(
        user_id=created_user1.id,
        url="https://test3.com",
    )
    with pytest.raises(NumPortfolioUrlLimitException):
        portfolio_url_service.create_portfolio_url(
            user_id=created_user1.id,
            url="https://test4.com",
        )


def test_create_portfolio_url_v2(
    created_user1: User,
    portfolio_url_service: PortfolioUrlService,
):
    response = portfolio_url_service.create_portfolio_url(
        user_id=created_user1.id,
        url="https://test1.com",
        term="20.5",
    )
    expected = PortfolioUrlResponse(
        id=4,
        url="https://test1.com",
        term="20.5",
    )
    assert response == expected

    portfolio_url_service.create_portfolio_url(
        user_id=created_user1.id,
        url="https://test2.com",
        term="20.5",
    )
    portfolio_url_service.create_portfolio_url(
        user_id=created_user1.id,
        url="https://test3.com",
        term="20.5",
    )
    with pytest.raises(NumPortfolioUrlLimitException):
        portfolio_url_service.create_portfolio_url(
            user_id=created_user1.id,
            url="https://test4.com",
            term="20.5",
        )
    portfolio_url_service.create_portfolio_url(
        user_id=created_user1.id,
        url="https://test3.com",
        term="21.5",
    )


def test_list_portfolio_urls(
    created_user1: User,
    created_user2: User,
    portfolio_url_service: PortfolioUrlService,
):
    portfolio1 = portfolio_url_service.create_portfolio_url(
        user_id=created_user1.id,
        url="https://test1.com",
    )
    portfolio2 = portfolio_url_service.create_portfolio_url(
        user_id=created_user1.id,
        url="https://test2.com",
    )
    portfolio3 = portfolio_url_service.create_portfolio_url(
        user_id=created_user2.id,
        url="https://test3.com",
    )
    response = portfolio_url_service.list_portfolio_urls(user_id=created_user1.id)
    expected = [
        PortfolioUrlResponse(
            id=portfolio1.id,
            url="https://test1.com",
        ),
        PortfolioUrlResponse(
            id=portfolio2.id,
            url="https://test2.com",
        ),
    ]
    assert response == expected

    response = portfolio_url_service.list_portfolio_urls(user_id=created_user2.id)
    expected = [
        PortfolioUrlResponse(
            id=portfolio3.id,
            url="https://test3.com",
        ),
    ]
    assert response == expected


def test_list_portfolio_urls_v2(
    created_user1: User,
    created_user2: User,
    portfolio_url_service: PortfolioUrlService,
):
    portfolio1 = portfolio_url_service.create_portfolio_url(
        user_id=created_user1.id,
        url="https://test1.com",
        term="20.5",
    )
    portfolio2 = portfolio_url_service.create_portfolio_url(
        user_id=created_user1.id,
        url="https://test2.com",
        term="21.5",
    )
    portfolio3 = portfolio_url_service.create_portfolio_url(
        user_id=created_user2.id,
        url="https://test3.com",
        term="21.5",
    )
    response = portfolio_url_service.list_portfolio_urls(
        user_id=created_user1.id, term="20.5"
    )
    expected = [
        PortfolioUrlResponse(
            id=portfolio1.id,
            url="https://test1.com",
            term="20.5",
        ),
    ]
    assert response == expected

    response = portfolio_url_service.list_portfolio_urls(
        user_id=created_user2.id, term="21.5"
    )
    expected = [
        PortfolioUrlResponse(
            id=portfolio3.id,
            url="https://test3.com",
            term="21.5",
        ),
    ]
    assert response == expected


def test_delete_portfolio_url(
    created_user1: User,
    created_user2: User,
    portfolio_url_service: PortfolioUrlService,
):
    portfolio1 = portfolio_url_service.create_portfolio_url(
        user_id=created_user1.id,
        url="https://test1.com",
    )
    portfolio2 = portfolio_url_service.create_portfolio_url(
        user_id=created_user2.id,
        url="https://test2.com",
    )
    portfolio_url_service.delete_portfolio_url(
        user_id=created_user1.id,
        portfolio_url_id=portfolio1.id,
    )
    response = portfolio_url_service.list_portfolio_urls(user_id=created_user1.id)
    expected = []
    assert response == expected

    with pytest.raises(PortfolioUrlNotFound):
        portfolio_url_service.delete_portfolio_url(
            user_id=created_user1.id,
            portfolio_url_id=1000,
        )
    with pytest.raises(PortfolioUrlNotAuthorized):
        portfolio_url_service.delete_portfolio_url(
            user_id=created_user1.id,
            portfolio_url_id=portfolio2.id,
        )


def test_delete_all_portfolio_urls(
    created_user1: User,
    portfolio_url_service: PortfolioUrlService,
):
    portfolio_url_service.create_portfolio_url(
        user_id=created_user1.id,
        url="https://test1.com",
    )

    portfolio_url_service.create_portfolio_url(
        user_id=created_user1.id,
        url="https://test2.com",
    )

    portfolio_url_service.delete_all_portfolio_urls(user_id=created_user1.id)
    response = portfolio_url_service.list_portfolio_urls(user_id=created_user1.id)
    expected = []
    assert response == expected


def test_update_portfolio_url(
    created_user1: User,
    created_user2: User,
    portfolio_url_service: PortfolioUrlService,
):
    portfolio1 = portfolio_url_service.create_portfolio_url(
        user_id=created_user1.id,
        url="https://test1.com",
    )
    portfolio2 = portfolio_url_service.create_portfolio_url(
        user_id=created_user2.id,
        url="https://test2.com",
    )
    portfolio_url_service.update_portfolio_url(
        user_id=created_user1.id,
        portfolio_url_id=portfolio1.id,
        url="https://test3.com",
    )
    response = portfolio_url_service.list_portfolio_urls(user_id=created_user1.id)
    expected = [
        PortfolioUrlResponse(
            id=portfolio1.id,
            url="https://test3.com",
        ),
    ]
    assert response == expected

    with pytest.raises(PortfolioUrlNotFound):
        portfolio_url_service.update_portfolio_url(
            user_id=created_user1.id,
            portfolio_url_id=1000,
            url="https://test3.com",
        )
    with pytest.raises(PortfolioUrlNotAuthorized):
        portfolio_url_service.update_portfolio_url(
            user_id=created_user1.id,
            portfolio_url_id=portfolio2.id,
            url="https://test3.com",
        )
