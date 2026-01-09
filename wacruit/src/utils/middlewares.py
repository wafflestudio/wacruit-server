from starlette.types import ASGIApp
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send


class HttpToHttpsRequestMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            scope["scheme"] = "https"
        elif scope["type"] == "websocket":
            scope["scheme"] = "wss"
        await self.app(scope, receive, send)
