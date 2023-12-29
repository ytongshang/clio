import logging
from typing import Optional, Sequence

from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .ctx import RequestContext
from .globals import request_context_manager
from .interceptor import Interceptor

_logger = logging.getLogger(__name__)


class RawContextMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        interceptors: Optional[Sequence[Interceptor]] = None,
        default_error_response: Response = Response(status_code=400),
    ) -> None:
        self.app = app
        self.interceptors = interceptors or []
        self.error_response = default_error_response

    async def process_request(self, request: Request):
        """You might want to override this method."""
        for interceptor in self.interceptors:
            await interceptor.process_request(request)

    # noinspection PyMethodMayBeStatic
    async def send_response(self, error_response: Response, send: Send) -> None:
        message_head = {
            "type": "http.response.start",
            "status": error_response.status_code,
            "headers": error_response.raw_headers,
        }
        await send(message_head)

        message_body = {
            "type": "http.response.body",
            "body": error_response.body,
        }
        await send(message_body)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive, send)

        with request_context_manager(RequestContext(request)):
            await self.process_request(request)

            async def send_wrapper(message: Message):
                for interceptor in reversed(self.interceptors):
                    await interceptor.process_response(message)
                await send(message)

            await self.app(scope, receive, send_wrapper)
