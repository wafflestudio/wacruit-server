import pytest

from wacruit.src.apps.portfolio.url.exceptions import NumPortfolioUrlLimitException
from wacruit.src.apps.portfolio.url.exceptions import PortfolioUrlNotAuthorized
from wacruit.src.apps.portfolio.url.exceptions import PortfolioUrlNotFound
from wacruit.src.apps.portfolio.url.schemas import PortfolioUrlResponse
from wacruit.src.apps.portfolio.url.services import PortfolioUrlService
from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.user.models import User


def test_create_portfolio_url(
    user1: User,
    recruiting1: Recruiting,
    recruiting2: Recruiting,
    portfolio_url_service: PortfolioUrlService,
):
    response = portfolio_url_service.create_portfolio_url(
        user_id=user1.id,
        url="https://test1.com",
        generation=recruiting1.id,
    )
    expected = PortfolioUrlResponse(
        id=response.id,
        url="https://test1.com",
        generation=recruiting1.id,
    )
    assert response == expected

    portfolio_url_service.create_portfolio_url(
        user_id=user1.id,
        url="https://test2.com",
        generation=recruiting1.id,
    )
    portfolio_url_service.create_portfolio_url(
        user_id=user1.id,
        url="https://test3.com",
        generation=recruiting1.id,
    )
    with pytest.raises(NumPortfolioUrlLimitException):
        portfolio_url_service.create_portfolio_url(
            user_id=user1.id,
            url="https://test4.com",
            generation=recruiting1.id,
        )
    portfolio_url_service.create_portfolio_url(
        user_id=user1.id,
        url="https://test3.com",
        generation=recruiting2.id,
    )


def test_list_portfolio_urls(
    user1: User,
    user2: User,
    recruiting1: Recruiting,
    recruiting2: Recruiting,
    portfolio_url_service: PortfolioUrlService,
):
    portfolio1 = portfolio_url_service.create_portfolio_url(
        user_id=user1.id,
        url="https://test1.com",
        generation=recruiting1.id,
    )
    portfolio2 = portfolio_url_service.create_portfolio_url(
        user_id=user1.id,
        url="https://test2.com",
        generation=recruiting2.id,
    )
    portfolio3 = portfolio_url_service.create_portfolio_url(
        user_id=user2.id,
        url="https://test3.com",
        generation=recruiting2.id,
    )
    response = portfolio_url_service.list_portfolio_urls(
        user_id=user1.id, generation=recruiting1.id
    )
    expected = [
        PortfolioUrlResponse(
            id=portfolio1.id,
            url="https://test1.com",
            generation=recruiting1.id,
        ),
    ]
    assert response == expected

    response = portfolio_url_service.list_portfolio_urls(
        user_id=user2.id, generation=recruiting2.id
    )
    expected = [
        PortfolioUrlResponse(
            id=portfolio3.id,
            url="https://test3.com",
            generation=recruiting2.id,
        ),
    ]
    assert response == expected


def test_delete_portfolio_url(
    user1: User,
    user2: User,
    recruiting1: Recruiting,
    portfolio_url_service: PortfolioUrlService,
):
    portfolio1 = portfolio_url_service.create_portfolio_url(
        user_id=user1.id,
        url="https://test1.com",
        generation=recruiting1.id,
    )
    portfolio2 = portfolio_url_service.create_portfolio_url(
        user_id=user2.id,
        url="https://test2.com",
        generation=recruiting1.id,
    )
    portfolio_url_service.delete_portfolio_url(
        user_id=user1.id,
        portfolio_url_id=portfolio1.id,
    )
    response = portfolio_url_service.list_portfolio_urls(
        user_id=user1.id, generation=recruiting1.id
    )
    expected = []
    assert response == expected

    with pytest.raises(PortfolioUrlNotFound):
        portfolio_url_service.delete_portfolio_url(
            user_id=user1.id,
            portfolio_url_id=1000,
        )
    with pytest.raises(PortfolioUrlNotAuthorized):
        portfolio_url_service.delete_portfolio_url(
            user_id=user1.id,
            portfolio_url_id=portfolio2.id,
        )


def test_delete_all_portfolio_urls(
    user1: User,
    recruiting1: Recruiting,
    portfolio_url_service: PortfolioUrlService,
):
    portfolio_url_service.create_portfolio_url(
        user_id=user1.id,
        url="https://test1.com",
        generation=recruiting1.id,
    )

    portfolio_url_service.create_portfolio_url(
        user_id=user1.id,
        url="https://test2.com",
        generation=recruiting1.id,
    )

    portfolio_url_service.delete_all_portfolio_urls(
        user_id=user1.id, generation=recruiting1.id
    )
    response = portfolio_url_service.list_portfolio_urls(
        user_id=user1.id, generation=recruiting1.id
    )
    expected = []
    assert response == expected


def test_update_portfolio_url(
    user1: User,
    user2: User,
    recruiting1: Recruiting,
    portfolio_url_service: PortfolioUrlService,
):
    portfolio1 = portfolio_url_service.create_portfolio_url(
        user_id=user1.id,
        url="https://test1.com",
        generation=recruiting1.id,
    )
    portfolio2 = portfolio_url_service.create_portfolio_url(
        user_id=user2.id,
        url="https://test2.com",
        generation=recruiting1.id,
    )
    portfolio_url_service.update_portfolio_url(
        user_id=user1.id,
        portfolio_url_id=portfolio1.id,
        url="https://test3.com",
    )
    response = portfolio_url_service.list_portfolio_urls(
        user_id=user1.id, generation=recruiting1.id
    )
    expected = [
        PortfolioUrlResponse(
            id=portfolio1.id,
            url="https://test3.com",
            generation=recruiting1.id,
        ),
    ]
    assert response == expected

    with pytest.raises(PortfolioUrlNotFound):
        portfolio_url_service.update_portfolio_url(
            user_id=user1.id,
            portfolio_url_id=1000,
            url="https://test3.com",
        )
    with pytest.raises(PortfolioUrlNotAuthorized):
        portfolio_url_service.update_portfolio_url(
            user_id=user1.id,
            portfolio_url_id=portfolio2.id,
            url="https://test3.com",
        )
