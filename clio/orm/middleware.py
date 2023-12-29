from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from .orm import SQLAlchemy


class SessionMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        sqlalchemy: SQLAlchemy,
    ):
        self.app = app
        self.sqlalchemy = sqlalchemy

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        req = Request(scope)
        try:
            session = self.sqlalchemy.SessionLocal()
            req.state.db = session
            await self.app(scope, receive, send)
        finally:
            req.state.db.close()
