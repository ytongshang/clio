from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

from clio import object_to_dict

T = TypeVar("T")


class HttpResponse(BaseModel, Generic[T]):
    code: int = Field(-1, description="错误码")
    message: str = Field("", description="错误信息")
    data: T = Field(..., description="返回数据")

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
            "data": object_to_dict(self.data) if self.data is not None else None,
        }
