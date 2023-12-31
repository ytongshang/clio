from typing import Generic, Optional, TypeVar

from clio.pydantics import BaseModel, Field
from clio.utils import object_to_json

T = TypeVar("T")


class HttpResponse(BaseModel, Generic[T]):
    code: int = Field(-1, description="错误码")
    message: str = Field("", description="错误信息")
    data: Optional[T] = Field(..., description="返回数据")

    @classmethod
    def success(cls, data: Optional[T] = None):
        return cls(code=0, message="", data=data)

    @classmethod
    def failure(cls, code: int, message: str):
        return cls(code=code, message=message, data=None)

    def to_json(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "data": object_to_json(self.data) if self.data is not None else None,
        }
