from __future__ import annotations

from typing import Any, Dict, Optional

from starlette.requests import Request


class RequestContext:
    key_request = "__request"

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from context."""
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        """Set value in context."""
        self._data[key] = value

    def remove(self, key: str) -> Any:
        """Remove value from context and return the old value."""
        self._data.pop(key, None)

    def copy(self) -> RequestContext:
        return self.__class__(
            data=self._data,
        )

    @property
    def request(self) -> Optional[Request]:
        return self.get(RequestContext.key_request, None)
