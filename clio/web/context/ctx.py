from __future__ import annotations

from typing import Any

from starlette.datastructures import State
from starlette.requests import Request


class RequestContext:
    def __init__(self, request: Request):
        self._request = request

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from context."""
        state: State = self._request.state
        if hasattr(state, key):
            return getattr(state, key, default)
        return default

    def set(self, key: str, value: Any):
        """Set value in context."""
        state = self._request.state
        setattr(state, key, value)

    def remove(self, key: str) -> Any:
        """Remove value from context and return the old value."""
        state: State = self._request.state
        if hasattr(state, key):
            return delattr(state, key)

    @property
    def request(self) -> Request:
        return self._request

    def copy(self) -> RequestContext:
        return self.__class__(
            request=self._request,
        )
