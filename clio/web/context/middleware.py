from typing import Dict

from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from .ctx import RequestContext
from .globals import request_context_manager
from .trace import trace_context


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
        trace_map: Dict[str, str] = trace_context.parse_trace_id(scope)
        for k, v in trace_map.items():
            request_context.set(k, v)

        with request_context_manager(request_context):
            await self.app(scope, receive, send)
