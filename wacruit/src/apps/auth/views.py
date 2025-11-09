from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from wacruit.src.apps.auth.schemas import LoginRequest
from wacruit.src.apps.auth.schemas import TokenResponse
from wacruit.src.apps.auth.services import AuthService

v3_router = APIRouter(prefix="/v3/auth", tags=["auth"])

security = HTTPBearer(scheme_name="refresh_token", description="토큰 갱신을 위한 Bearer 토큰")


@v3_router.post("/login")
def login(
    req: LoginRequest, auth_service: Annotated[AuthService, Depends()]
) -> TokenResponse:
    res = auth_service.login(req.username, req.password)

    return TokenResponse(access_token=res[0], refresh_token=res[1])


@v3_router.post("/refresh")
def refresh_token(
    refresh_credentials: Annotated[HTTPAuthorizationCredentials, Security(security)],
    auth_service: Annotated[AuthService, Depends()],
) -> TokenResponse:
    res = auth_service.refresh_token(refresh_credentials.credentials)

    return TokenResponse(access_token=res[0], refresh_token=res[1])
