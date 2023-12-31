from typing import Optional


class BusinessException(Exception):
    def __init__(self, code: int, message: str = "", cause: Optional[Exception] = None):
        self.code = code
        self.message = message
        self.cause = cause

    @classmethod
    def from_error(cls, error):
        return cls(error.code, error.message)

    def __str__(self):
        if self.cause is None:
            return f"BusinessException, code: {self.code}, message: {self.message}"
        return f"BusinessException, code: {self.code}, message: {self.message}, cause: {self.cause}"
