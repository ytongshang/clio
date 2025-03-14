from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Any, Dict, Iterator

from starlette.requests import Request

from .ctx import RequestContext
from .errors import ContextDoesNotExistError

_request_scope_context_storage: ContextVar[RequestContext] = ContextVar(
    "clio_request_context"
)


@contextmanager
def request_context_manager(
    initial_data: RequestContext,
) -> Iterator[None]:
    """Creates and resets a starlette-context context.

    Used in the Context and Raw middlewares, but can also be used to
    create a context out of a proper request cycle, such as in unit
    tests.
    """
    token: Token = _request_scope_context_storage.set(initial_data.copy())
    yield
    _request_scope_context_storage.reset(token)


def has_request_context() -> bool:
    """Check if request context exists."""
    return _request_scope_context_storage.get(None) is not None


def request_context() -> RequestContext:
    value = _request_scope_context_storage.get(None)
    if value is None:
        raise ContextDoesNotExistError()
    return value


def request() -> Request:
    return request_context().request


def request_context_update(data: Dict[str, Any]):
    if not has_request_context():
        return
    ctx = request_context()
    for key, value in data.items():
        ctx.set(key, value)
