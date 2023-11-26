from typing import Optional


class RpcException(Exception):
    def __init__(self, message: str, cause: Optional[Exception] = None):
        self.message = message
        self.cause = cause

    def __str__(self):
        if self.cause is None:
            return f" RpcException message: {self.message}"
        return f"RpcException message: {self.message}, cause: {str(self.cause)}"
