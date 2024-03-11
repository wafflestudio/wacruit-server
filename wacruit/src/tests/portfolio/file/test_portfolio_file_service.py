import moto
import pytest

from wacruit.src.apps.portfolio.file.exceptions import NumPortfolioLimitException
from wacruit.src.apps.portfolio.file.schemas import PortfolioFileResponse
from wacruit.src.apps.portfolio.file.schemas import PresignedUrlWithIdResponse
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
    expected = PresignedUrlWithIdResponse(
        object_name=f"{recruiting1.id}/{user1.id}/test1.pdf",
        presigned_url="https://wacruit-portfolio-test.s3.amazonaws.com/",
        fields={
            "key": f"{recruiting1.id}/{user1.id}/test1.pdf",
            "x-amz-algorithm": "AWS4-HMAC-SHA256",
            "x-amz-credential": "FOOBARKEY/20231105/ap-northeast-2/s3/aws4_request",
            "x-amz-date": "20231105T094622Z",
            "policy": "Random Policy",
            "x-amz-signature": "Random Signature",
        },
        portfolio_file_id=response.portfolio_file_id,
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

    # pylint: disable=line-too-long
    assert (
        url
        == f"https://wacruit-portfolio-test.s3.amazonaws.com/{recruiting1.id}/{user1.id}/test1.pdf"
    )


@moto.mock_s3
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
    s3_client.create_bucket(
        Bucket="wacruit-portfolio-test",
        CreateBucketConfiguration={"LocationConstraint": "ap-northeast-2"},
    )
    s3_client.put_object(
        Bucket="wacruit-portfolio-test",
        Key=f"{recruiting1.id}/{user1.id}/test1.pdf",
    )
    portfolio_file_service.delete_portfolio(
        user_id=user1.id,
        portfolio_file_id=response.portfolio_file_id,
    )

    response = portfolio_file_service.list_portfolios_from_db(
        user_id=user1.id,
        recruiting_id=recruiting1.id,
    )
    expected = []
    assert response == expected
