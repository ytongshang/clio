from typing import Any

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Query
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.requests import Request

from clio.web import request


class SQLAlchemy:
    def __init__(
        self,
        database_uri: str,
        session_options: dict[str, Any] | None = None,
        engine_options: dict[str, Any] | None = None,
        echo: bool = False,
        async_mode: bool = False,
    ):
        self.async_mode = async_mode
        # create engine
        if async_mode:
            engine = create_async_engine(
                database_uri,
                echo=echo,
                **(engine_options or {}),
            )

            def _async_session_maker() -> AsyncSession:
                return AsyncSession(engine, **(session_options or {}))

            self.engine = engine
            self.SQLModel = SQLModel
            self.SessionMaker = _async_session_maker
        else:
            engine = create_engine(
                database_uri,
                echo=echo,
                **(engine_options or {}),
            )

            def _session_maker() -> Session:
                return Session(engine, **(session_options or {}))

            self.engine = engine
            self.SQLModel = SQLModel
            self.SessionMaker = _session_maker

    def create_all(self):
        if self.async_mode:
            raise RuntimeError("async_mode, use create_all_async instead")
        self.SQLModel.metadata.create_all(bind=self.engine)

    def drop_all(self):
        if self.async_mode:
            raise RuntimeError("async_mode, use drop_all_async instead")
        self.SQLModel.metadata.drop_all(bind=self.engine)

    async def create_all_async(self):
        if not self.async_mode:
            raise RuntimeError("not async_mode, use create_all instead")
        async with self.engine.begin() as conn:
            await conn.run_sync(self.SQLModel.metadata.create_all)

    async def drop_all_async(self):
        if not self.async_mode:
            raise RuntimeError("not async_mode, use drop_all instead")
        async with self.engine.begin() as conn:
            await conn.run_sync(self.SQLModel.metadata.drop_all)

    @property
    def session(self) -> Session:
        if self.async_mode:
            raise RuntimeError("async_mode, use async_session instead")
        req: Request = request()
        state = req.state
        if hasattr(state, "db_session"):
            return req.state.db_session
        else:
            req.state.db_session = self.SessionMaker()
            return req.state.db_session

    # noinspection PyTypeChecker
    @property
    def async_session(self) -> AsyncSession:
        if not self.async_mode:
            raise RuntimeError("not async_mode, use session instead")
        req: Request = request()
        state = req.state
        if hasattr(state, "db_session"):
            return req.state.db_session
        else:
            req.state.db_session = self.SessionMaker()
            return req.state.db_session

    def get_session(self):
        if self.async_mode:
            raise RuntimeError("async_mode, use get_async_session instead")
        with self.SessionMaker() as session:
            yield session

    async def get_async_session(self):
        if not self.async_mode:
            raise RuntimeError("not async_mode, use get_session instead")
        async with self.SessionMaker() as session:
            yield session

    def query(self, *entities, **kwargs) -> Query:
        """使用老的SqlAlchemy的query方法"""
        if self.async_mode:
            raise RuntimeError("async_mode does not support query method")
        _session = self.session
        return _session.query(*entities, **kwargs)
