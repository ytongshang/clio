from typing import Optional

from sqlmodel import Field, SQLModel


class Hero(SQLModel, table=True):  # type: ignore
    __tablename__ = "hero"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., description="姓名")
    secret_name: str = Field(..., description="秘密姓名")
    age: Optional[int] = Field(default=None, description="年龄")
