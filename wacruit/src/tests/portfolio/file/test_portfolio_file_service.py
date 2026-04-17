from urllib.parse import urlparse

from botocore.exceptions import ClientError
import pytest

from wacruit.src.apps.portfolio.file.aws.config import storage_config
from wacruit.src.apps.portfolio.file.exceptions import NumPortfolioLimitException
from wacruit.src.apps.portfolio.file.schemas import PortfolioFileResponse
from wacruit.src.apps.portfolio.file.services_v2 import PortfolioFileService
from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.user.models import User


def test_get_upload_portfolio_file_v2(
    user1: User,
    recruiting1: Recruiting,
    portfolio_file_service: PortfolioFileService,
):
    response = portfolio_file_service.get_presigned_url_for_post_portfolio(
        user_id=user1.id,
        file_name="test1.pdf",
        recruiting_id=recruiting1.id,
    )
    expected_object_name = f"{recruiting1.id}/{user1.id}/test1.pdf"
    expected_url = (
        f"{storage_config.endpoint_url}/{storage_config.bucket_name}"
        if storage_config.endpoint_url
        else f"https://s3.{storage_config.region}.amazonaws.com/{storage_config.bucket_name}"
    )

    assert response.object_name == expected_object_name
    assert response.portfolio_file_id > 0
    assert response.presigned_url == expected_url
    assert response.fields["key"] == expected_object_name
    assert response.fields["x-amz-algorithm"] == "AWS4-HMAC-SHA256"
    assert response.fields["x-amz-credential"].endswith(
        f"/{storage_config.region}/s3/aws4_request"
    )
    assert "x-amz-date" in response.fields
    assert "policy" in response.fields
    assert "x-amz-signature" in response.fields


def test_register_portfolio_file_v2(
    user1: User,
    recruiting1: Recruiting,
    recruiting2: Recruiting,
    portfolio_file_service: PortfolioFileService,
):
    response = portfolio_file_service.get_presigned_url_for_post_portfolio(
        user_id=user1.id,
        file_name="test1.pdf",
        recruiting_id=recruiting1.id,
    )
    response = portfolio_file_service.register_portfolio_file_info_in_db(
        user1.id, response.portfolio_file_id
    )
    first_id = response.id
    expected = PortfolioFileResponse(
        id=first_id,
        file_name="test1.pdf",
        recruiting_id=recruiting1.id,
        is_uploaded=True,
    )
    assert response == expected

    with pytest.raises(NumPortfolioLimitException):
        response = portfolio_file_service.get_presigned_url_for_post_portfolio(
            user_id=user1.id,
            file_name="test2.pdf",
            recruiting_id=recruiting1.id,
        )
        portfolio_file_service.register_portfolio_file_info_in_db(
            user1.id, response.portfolio_file_id
        )

    response = portfolio_file_service.get_presigned_url_for_post_portfolio(
        user_id=user1.id,
        file_name="test2.pdf",
        recruiting_id=recruiting2.id,
    )
    portfolio_file_service.register_portfolio_file_info_in_db(
        user1.id, response.portfolio_file_id
    )

    response = portfolio_file_service.list_portfolios_from_db(
        user_id=user1.id,
        recruiting_id=recruiting1.id,
    )
    expected = [
        PortfolioFileResponse(
            id=first_id,
            file_name="test1.pdf",
            recruiting_id=recruiting1.id,
            is_uploaded=True,
        ),
    ]
    assert response == expected, response


def test_get_download_portfolio_file_url_v2(
    user1: User,
    recruiting1: Recruiting,
    portfolio_file_service: PortfolioFileService,
):
    response = portfolio_file_service.get_presigned_url_for_post_portfolio(
        user_id=user1.id,
        file_name="test1.pdf",
        recruiting_id=recruiting1.id,
    )
    portfolio_file_service.register_portfolio_file_info_in_db(
        user1.id, response.portfolio_file_id
    )
    response = portfolio_file_service.get_presigned_url_for_get_portfolio(
        user_id=user1.id,
        portfolio_file_id=response.portfolio_file_id,
    )
    url, _ = response.presigned_url.split("?")

    parsed = urlparse(url)
    expected_path = (
        f"/{storage_config.bucket_name}/{recruiting1.id}/{user1.id}/test1.pdf"
    )

    if storage_config.endpoint_url:
        endpoint = urlparse(storage_config.endpoint_url)
        assert parsed.scheme == endpoint.scheme
        assert parsed.netloc == endpoint.netloc
        assert parsed.path == expected_path
    else:
        assert parsed.scheme == "https"
        assert parsed.netloc == f"s3.{storage_config.region}.amazonaws.com"
        assert parsed.path == expected_path


def test_delete_portfolio_file_v2(
    user1: User,
    recruiting1: Recruiting,
    portfolio_file_service: PortfolioFileService,
):
    response = portfolio_file_service.get_presigned_url_for_post_portfolio(
        user_id=user1.id,
        file_name="test1.pdf",
        recruiting_id=recruiting1.id,
    )

    portfolio_file_service.register_portfolio_file_info_in_db(
        user1.id, response.portfolio_file_id
    )
    s3_client = portfolio_file_service._s3_client.client
    s3_client.put_object(
        Bucket=storage_config.bucket_name,
        Key=f"{recruiting1.id}/{user1.id}/test1.pdf",
        Body=b"portfolio-delete-test",
    )
    portfolio_file_service.delete_portfolio(
        user_id=user1.id,
        portfolio_file_id=response.portfolio_file_id,
    )

    with pytest.raises(ClientError):
        s3_client.head_object(
            Bucket=storage_config.bucket_name,
            Key=f"{recruiting1.id}/{user1.id}/test1.pdf",
        )

    response = portfolio_file_service.list_portfolios_from_db(
        user_id=user1.id,
        recruiting_id=recruiting1.id,
    )
    expected = []
    assert response == expected
