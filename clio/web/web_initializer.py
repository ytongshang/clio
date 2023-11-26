from typing import Any, Literal

from flask import Flask, has_request_context, request

from clio.utils.log import Log

from .exception.business_exception import BusinessException
from .exception.param_exception import ParamException
from .exception.rpc_exception import RpcException
from .http_response import HttpResponse
from .swagger import FlaskPydanticSpec


def exception_handler(
    application: Flask, server_error_code: int = 500, rpc_error_code: int = 500
):
    @application.errorhandler(BusinessException)
    def business_error_handler(error):
        Log.error("business error: %s", error)
        return HttpResponse.failure(error.code, error.message).to_json()

    @application.errorhandler(RpcException)
    def rpc_error_handler(error):
        Log.error("rpc error: %s", error)
        return HttpResponse.failure(rpc_error_code, error.message).to_json()

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


def http_query():
    return http_value_or_throw("query")


def http_body():
    return http_value_or_throw("body")


def http_headers():
    return http_value_or_throw("headers")


def http_cookies():
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
    return api_validator
