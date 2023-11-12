from typing import Any, Literal

from flask import Flask
from flask import Request as FlaskRequest
from flask import has_request_context, request

from clio.utils.log import Log

from .exception.business_exception import BusinessException
from .exception.param_exception import ParamException
from .http_response import HttpResponse
from .swagger import FlaskPydanticSpec


def exception_handler(application: Flask, server_error_code: int = 500):
    @application.errorhandler(BusinessException)
    def business_error_handler(error):
        Log.error("business error: %s", error)
        return HttpResponse.failure(error.code, error.message).to_json()

    @application.errorhandler(Exception)
    def custom_error_handler(error):
        Log.error("custom error: %s", error)
        return HttpResponse.failure(server_error_code, str(error)).to_json()


def http_value(name: Literal["query", "body", "headers", "cookies"]):
    if has_request_context():
        http_context = getattr(request, "http_context", None)
        if http_context:
            return getattr(http_context, name)
    return None


def http_value_or_throw(name: Literal["query", "body", "headers", "cookies"]):
    value = http_value(name)
    if value is None:
        raise ParamException(f"{name} is None")
    return value


def query():
    return http_value_or_throw("query")


def body():
    return http_value_or_throw("body")


def headers():
    return http_value_or_throw("headers")


def cookies():
    return http_value_or_throw("cookies")


def swagger_api(
    backend_name="base",
    title="Flask",
    version="0.0.1",
    **kwargs: Any,
) -> FlaskPydanticSpec:
    # api validator
    api_validator = FlaskPydanticSpec(
        backend_name, title=title, version=version, **kwargs
    )

    def __http_query(self):
        http_context = getattr(self, "http_context", None)
        if http_context:
            return http_context.query
        return None

    def __http_body(self):
        http_context = getattr(self, "http_context", None)
        if http_context:
            return http_context.body
        return None

    def __http_headers(self):
        http_context = getattr(self, "http_context", None)
        if http_context:
            return http_context.headers
        return None

    def __http_cookies(self):
        http_context = getattr(self, "http_context", None)
        if http_context:
            return http_context.cookies
        return None

    FlaskRequest.http_query = __http_query
    FlaskRequest.http_body = __http_body
    FlaskRequest.http_headers = __http_headers
    FlaskRequest.http_cookies = __http_cookies

    return api_validator
