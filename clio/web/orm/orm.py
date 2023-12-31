from typing import Any, Callable

from sqlalchemy import Engine
from sqlalchemy.orm import Query
from sqlmodel import Session, SQLModel, create_engine
from starlette.requests import Request

from clio.web import request


class SQLAlchemy:
    def __init__(
        self,
        database_uri: str,
        session_options: dict[str, Any] | None = None,
        engine_options: dict[str, Any] | None = None,
        echo: bool = False,
    ):
        # create engine
        self.engine: Engine = create_engine(
            database_uri,
            echo=echo,
            **(engine_options or {}),
        )

        # Define a SQLModel base class
        self.SQLModel = SQLModel

        def _session_maker() -> Session:
            return Session(self.engine, **(session_options or {}))

        # Define a SessionMaker method
        self.SessionMaker: Callable[[], Session] = _session_maker

    def create_all(self):
        self.SQLModel.metadata.create_all(bind=self.engine)

    def drop_all(self):
        self.SQLModel.metadata.drop_all(bind=self.engine)

    @property
    def session(self) -> Session:
        req: Request = request()
        state = req.state
        if hasattr(state, "db_session"):
            return req.state.db_session
        else:
            req.state.db_session = self.SessionMaker()
            return req.state.db_session

    def query(self, *entities, **kwargs) -> Query:
        """使用老的SqlAlchemy的query方法"""
        _session = self.session
        return _session.query(*entities, **kwargs)
