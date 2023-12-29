from fastapi import FastAPI

from clio.utils.log import Log

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
    def not_found_error_handler(request, exc):
        url = request.url
        msg = f"404 not found: {url}"
        Log.error(msg, exc_info=False)
        return HttpResponse.failure(not_found_code, msg).to_json()

    @application.exception_handler(BusinessException)
    def business_error_handler(request, exc):
        Log.error(f"business error: {exc}")
        return HttpResponse.failure(exc.code, exc.message).to_json()

    @application.exception_handler(RpcException)
    def rpc_error_handler(request, exc):
        Log.error(f"rpc error: {exc}")
        return HttpResponse.failure(rpc_error_code, exc.message).to_json()

    @application.exception_handler(Exception)
    def custom_error_handler(request, exc):
        error_msg = str(exc)
        Log.error(f"custom error: {error_msg}")
        return HttpResponse.failure(server_error_code, error_msg).to_json()
