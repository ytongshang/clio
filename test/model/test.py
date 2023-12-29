from pydantic import BaseModel, Field


class TestQuery(BaseModel):
    a: int = Field(..., description="a")


class TestBody(BaseModel):
    b: int = Field(..., description="b")


class TestHeaders(BaseModel):
    C: str = Field(..., description="c")


class TestCookies(BaseModel):
    d: str = Field(..., description="d")


class TestResp(BaseModel):
    e: str = Field(..., description="e")
