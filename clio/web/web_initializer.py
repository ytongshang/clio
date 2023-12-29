from fastapi import FastAPI
from starlette.requests import Request

from clio.utils.log import Log

from .context import request
from .exception.business_exception import BusinessException
from .exception.rpc_exception import RpcException
from .http_response import HttpResponse


def exception_handler(
    application: FastAPI,
    server_error_code: int = 500,
    rpc_error_code: int = 500,
    not_found_code: int = 404,
):
    @application.exception_handler(404)
    def not_found_error_handler(error):
        req: Request = request()
        url = req.url
        Log.error(f"404 not found: {req.url}", exc_info=False)
        return HttpResponse.failure(not_found_code, f"路由错误: {url}").to_json()

    @application.exception_handler(BusinessException)
    def business_error_handler(error):
        Log.error(f"business error: {error}")
        return HttpResponse.failure(error.code, error.message).to_json()

    @application.exception_handler(RpcException)
    def rpc_error_handler(error):
        Log.error("rpc error: %s", error)
        return HttpResponse.failure(rpc_error_code, error.message).to_json()

    @application.exception_handler(Exception)
    def custom_error_handler(error):
        Log.error(f"custom error: %s, error_details:{error}")
        return HttpResponse.failure(server_error_code, str(error)).to_json()
