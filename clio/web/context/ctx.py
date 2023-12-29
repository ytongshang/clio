from __future__ import annotations

from typing import Any, Dict, Optional

from starlette.requests import Request

from clio.web.context.errors import ContextDoesNotExistError


class RequestContext:
    def __init__(self, request: Request, data: Optional[Dict[str, Any]] = None):  # noqa
        self.data: Dict[str, Any] = data or {}
        self._request = request

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from context."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set value in context."""
        self.data[key] = value

    def remove(self, key: str) -> None:
        """Remove value from context."""
        self.data.pop(key, None)

    @property
    def request(self) -> Request:
        return self._request

    def copy(self) -> RequestContext:
        return self.__class__(
            data=self.data.copy(),
            request=self._request,
        )

    def __repr__(self) -> str:
        # Opaque type to avoid default implementation
        # that could try to look into data while out of request cycle
        try:
            return f"<{__name__}.{self.__class__.__name__} {self.data}>"
        except ContextDoesNotExistError:
            return f"<{__name__}.{self.__class__.__name__} {dict()}>"

    def __str__(self):
        try:
            return str(self.data)
        except ContextDoesNotExistError:
            return str({})
