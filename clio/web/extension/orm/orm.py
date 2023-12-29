from typing import Any

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from starlette.requests import Request

from clio.web import request


class SQLAlchemy:
    def __init__(
        self,
        database_uri: str,
        session_options: dict[str, Any] | None = None,
        engine_options: dict[str, Any] | None = None,
    ):
        # create engine
        self.engine: Engine = create_engine(
            database_uri,
            **(engine_options or {}),
        )

        # Model
        self.Model = declarative_base()

        # Session
        session_options = session_options or {}
        self.SessionLocal = sessionmaker(self.engine, **session_options)

    def create_all(self):
        self.Model.metadata.create_all(bind=self.engine)

    def drop_all(self):
        self.Model.metadata.drop_all(bind=self.engine)

    @property
    def session(self):
        req: Request = request()
        return req.state.db
