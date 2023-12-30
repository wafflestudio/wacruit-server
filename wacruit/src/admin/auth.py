from datetime import datetime
from datetime import timedelta

import jwt
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from wacruit.src.admin.config import admin_config

ALGORITHM = "HS256"


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not (isinstance(username, str) and isinstance(password, str)):
            return False

        authenticated = (
            username == admin_config.username and password == admin_config.password
        )

        if not authenticated:
            return False

        request.session["token"] = self.generate_jwt(username)
        return authenticated

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        return token is not None and self.verify_jwt(token)

    @staticmethod
    def generate_jwt(username: str) -> str:
        expires_at = datetime.utcnow() + timedelta(seconds=admin_config.expires_in)
        payload = {
            "sub": username,
            "exp": expires_at,
        }
        jwt_token = jwt.encode(payload, admin_config.password, algorithm=ALGORITHM)
        return jwt_token

    @staticmethod
    def verify_jwt(token: str) -> bool:
        try:
            payload = jwt.decode(token, admin_config.password, algorithms=[ALGORITHM])
            if payload["sub"] != admin_config.username:
                return False
            if datetime.utcfromtimestamp(payload["exp"]) < datetime.utcnow():
                return False
            return True
        except BaseException:
            return False


authentication_backend = AdminAuth(secret_key=admin_config.password)
