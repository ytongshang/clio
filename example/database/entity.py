from sqlalchemy import Boolean, Column, Integer, String

from example.database.database import db


class User(db.Model):  # type: ignore
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(64), unique=True, index=True)
    hashed_password = Column(String(64))
    is_active = Column(Boolean, default=True)
