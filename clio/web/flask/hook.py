from flask import Flask
from flask.typing import ResponseReturnValue

from clio import HttpResponse


def hook_make_response():
    _old_make_response = Flask.make_response

    def make_response(self, rv: ResponseReturnValue):
        return_value = rv
        if isinstance(rv, HttpResponse):
            return_value = rv.to_json()
        return _old_make_response(self, rv=return_value)

    Flask.make_response = make_response
