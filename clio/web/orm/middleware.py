from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession
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

        req = Request(scope, receive=receive, send=send)
        try:
            await self.app(scope, receive, send)
        finally:
            state = req.state
            if hasattr(state, "db_session"):
                session = state.db_session
                if isinstance(session, AsyncSession):
                    await session.close()
                if isinstance(session, Session):
                    session.close()
