from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from .ctx import RequestContext
from .globals import request_async_context_manager


class RawContextMiddleware:
    def __init__(
            self,
            app: ASGIApp,
    ):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return
        request = Request(scope, receive, send)
        context = RequestContext({RequestContext.key_request: request})
        async with request_async_context_manager(context):
            await self.app(scope, receive, send)
