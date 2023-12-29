from __future__ import annotations

from typing import Any, Dict, Optional

from starlette.requests import Request


class RequestContext:
    def __init__(self, request: Request, data: Optional[Dict[str, Any]] = None):
        self._data: Dict[str, Any] = data or {}
        self._request = request

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from context."""
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        """Set value in context."""
        self._data[key] = value

    def remove(self, key: str) -> Any:
        """Remove value from context and return the old value."""
        return self._data.pop(key, None)

    @property
    def request(self) -> Request:
        return self._request

    def copy(self) -> RequestContext:
        return self.__class__(
            request=self._request,
            data=self._data.copy(),
        )

    def __str__(self):
        return str(self._data)
