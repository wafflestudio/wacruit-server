import boto3
import moto
import pytest

from wacruit.src.apps.portfolio.file.exceptions import NumPortfolioLimitException
from wacruit.src.apps.portfolio.file.schemas import PortfolioFileResponse
from wacruit.src.apps.portfolio.file.schemas import PortfolioNameResponse
from wacruit.src.apps.portfolio.file.schemas import PresignedUrlResponse
from wacruit.src.apps.portfolio.file.services_v2 import PortfolioFileService
from wacruit.src.apps.user.models import User


def test_get_upload_portfolio_file_v2(
    created_user1: User,
    portfolio_file_service: PortfolioFileService,
):
    response = portfolio_file_service.get_presigned_url_for_post_portfolio(
        user_id=created_user1.id,
        file_name="test1.pdf",
        term="20.5",
    )
    expected = PresignedUrlResponse(
        object_name=f"20.5/{created_user1.id}/test1.pdf",
        presigned_url="https://test-bucket.s3.amazonaws.com/",
        fields={
            "key": f"20.5/{created_user1.id}/test1.pdf",
            "x-amz-algorithm": "AWS4-HMAC-SHA256",
            "x-amz-credential": "FOOBARKEY/20231105/ap-northeast-2/s3/aws4_request",
            "x-amz-date": "20231105T094622Z",
            "policy": "Random Policy",
            "x-amz-signature": "Random Signature",
        },
    )
    response.fields.update(
        {
            "x-amz-credential": "FOOBARKEY/20231105/ap-northeast-2/s3/aws4_request",
            "x-amz-date": "20231105T094622Z",
            "policy": "Random Policy",
            "x-amz-signature": "Random Signature",
        }
    )
    assert response == expected


def test_register_portfolio_file_v2(
    created_user1: User,
    portfolio_file_service: PortfolioFileService,
):
    response = portfolio_file_service.register_portfolio_file_info_in_db(
        created_user1.id, "test1.pdf", "20.5"
    )
    expected = PortfolioFileResponse(
        id=1,
        file_name="test1.pdf",
        term="20.5",
    )
    assert response == expected

    with pytest.raises(NumPortfolioLimitException):
        portfolio_file_service.register_portfolio_file_info_in_db(
            created_user1.id, "test2.pdf", "20.5"
        )

    portfolio_file_service.register_portfolio_file_info_in_db(
        created_user1.id, "test3.pdf", "21.5"
    )

    response = portfolio_file_service.list_portfolios_from_db(
        user_id=created_user1.id,
        term="20.5",
    )
    expected = [
        PortfolioFileResponse(
            id=1,
            file_name="test1.pdf",
            term="20.5",
        ),
    ]
    assert response == expected
    response = portfolio_file_service.update_portfolio_file_info_in_db(
        user_id=created_user1.id, portfolio_file_id=1, new_file_name="test2.pdf"
    )
    expected = PortfolioFileResponse(
        id=1,
        file_name="test2.pdf",
        term="20.5",
    )
    assert response == expected


def test_get_download_portfolio_file_url_v2(
    created_user1: User,
    portfolio_file_service: PortfolioFileService,
):
    portfolio_file_service.register_portfolio_file_info_in_db(
        created_user1.id, "test1.pdf", "20.5"
    )
    response = portfolio_file_service.get_presigned_url_for_get_portfolio(
        user_id=created_user1.id,
        portfolio_file_id=3,
    )
    url, _ = response.presigned_url.split("?")
    assert (
        url == f"https://test-bucket.s3.amazonaws.com/20.5/{created_user1.id}/test1.pdf"
    )


@moto.mock_s3
def test_delete_portfolio_file_v2(
    created_user1: User,
    portfolio_file_service: PortfolioFileService,
):
    portfolio_file_service.register_portfolio_file_info_in_db(
        created_user1.id, "test1.pdf", "20.5"
    )
    s3_client = portfolio_file_service._s3_client.client
    s3_client.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={"LocationConstraint": "ap-northeast-2"},
    )
    s3_client.put_object(
        Bucket="test-bucket",
        Key=f"20.5/{created_user1.id}/test1.pdf",
    )
    portfolio_file_service.delete_portfolio(
        user_id=created_user1.id,
        portfolio_file_id=4,
    )

    response = portfolio_file_service.list_portfolios_from_db(
        user_id=created_user1.id,
        term="20.5",
    )
    expected = []
    assert response == expected
