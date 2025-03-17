from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from clio.context import RequestContext, request_context_manager
from clio.context.trace import trace_context


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
        request_context = RequestContext(request)
        m = trace_context.parse_trace_id(scope, context=request_context)
        with request_context_manager(request_context):
            await self.app(scope, receive, send)
