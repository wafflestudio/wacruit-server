from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from wacruit.src.apps.auth.exceptions import EmailConflictException
from wacruit.src.apps.auth.exceptions import ExpiredPasswordResetCodeException
from wacruit.src.apps.auth.exceptions import InvalidPasswordResetCodeException
from wacruit.src.apps.auth.exceptions import PasswordResetCodeNotVerifiedException
from wacruit.src.apps.auth.exceptions import UserNotFoundException
from wacruit.src.apps.auth.schemas import LoginRequest
from wacruit.src.apps.auth.schemas import PasswordResetEmailRequest
from wacruit.src.apps.auth.schemas import PasswordResetRequest
from wacruit.src.apps.auth.schemas import PasswordResetVerifyRequest
from wacruit.src.apps.auth.schemas import TokenResponse
from wacruit.src.apps.auth.schemas import UserCheckRequest
from wacruit.src.apps.auth.services import AuthService
from wacruit.src.apps.common.exceptions import responses_from
from wacruit.src.apps.mail.exceptions import MailConfigException
from wacruit.src.apps.mail.exceptions import MailSendFailedException

v3_router = APIRouter(prefix="/v3/auth", tags=["auth"])

security = HTTPBearer(
    scheme_name="refresh_token", description="토큰 갱신을 위한 Bearer 토큰"
)


@v3_router.post("/login")
def login(
    req: LoginRequest, auth_service: Annotated[AuthService, Depends()]
) -> TokenResponse:
    res = auth_service.login(req.email, req.password)

    return TokenResponse(access_token=res[0], refresh_token=res[1])


@v3_router.post("/refresh")
def refresh_token(
    refresh_credentials: Annotated[HTTPAuthorizationCredentials, Security(security)],
    auth_service: Annotated[AuthService, Depends()],
) -> TokenResponse:
    res = auth_service.refresh_token(refresh_credentials.credentials)

    return TokenResponse(access_token=res[0], refresh_token=res[1])


@v3_router.post("/check", status_code=200)
def check_available_email(
    req: UserCheckRequest, auth_service: Annotated[AuthService, Depends()]
) -> None:
    res = auth_service.check_available_email(req.email)
    if not res:
        raise EmailConflictException()


@v3_router.post(
    "/password-reset/email",
    status_code=200,
    responses=responses_from(MailConfigException, MailSendFailedException),
)
def send_password_reset_email(
    req: PasswordResetEmailRequest,
    auth_service: Annotated[AuthService, Depends()],
) -> None:
    auth_service.send_password_reset_email(req.email)


@v3_router.post(
    "/password-reset/verify",
    status_code=200,
    responses=responses_from(
        InvalidPasswordResetCodeException,
        ExpiredPasswordResetCodeException,
    ),
)
def verify_password_reset_code(
    req: PasswordResetVerifyRequest,
    auth_service: Annotated[AuthService, Depends()],
) -> None:
    auth_service.verify_password_reset_code(req.email, req.code)


@v3_router.post(
    "/password-reset",
    status_code=200,
    responses=responses_from(
        InvalidPasswordResetCodeException,
        ExpiredPasswordResetCodeException,
        PasswordResetCodeNotVerifiedException,
        UserNotFoundException,
    ),
)
def reset_password(
    req: PasswordResetRequest,
    auth_service: Annotated[AuthService, Depends()],
) -> None:
    auth_service.reset_password(req.email, req.code, req.new_password)
