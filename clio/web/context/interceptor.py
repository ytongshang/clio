import abc

from starlette.requests import Request
from starlette.types import Message


class Interceptor(metaclass=abc.ABCMeta):
    """Base class for building those plugins to extract things from request.

    One plugin should be responsible for extracting one thing.
    key: the key that allows to access value in headers
    """

    async def process_request(self, request: Request):
        """Runs always on request.

        Extracts value from header by default.
        """

    async def process_response(self, response: Message):
        """Runs always on response.

        Does nothing by default.
        """
