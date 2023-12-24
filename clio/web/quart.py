from quart import Quart

from .http_response import HttpResponse


def hook_make_response():
    _old_make_response = Quart.make_response

    async def make_response(self, result):
        return_value = result
        if isinstance(return_value, HttpResponse):
            return_value = result.to_json()
        return await _old_make_response(self, result=return_value)

    Quart.make_response = make_response
