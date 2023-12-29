from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse, RedirectResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from clio.utils.log import Log

from .exception.business_exception import BusinessException
from .exception.rpc_exception import RpcException
from .http_response import HttpResponse


def register_exception_handler(
    application: FastAPI,
    server_error_code: int = 500,
    rpc_error_code: int = 500,
):
    @application.exception_handler(404)
    async def not_found_error_handler(request, exc):
        url = request.url
        msg = f"404 not found: {url}"
        Log.error(msg, exc_info=False)
        return JSONResponse(
            status_code=HTTP_404_NOT_FOUND,
            content=HttpResponse.failure(HTTP_404_NOT_FOUND, msg),
        )

    @application.exception_handler(RequestValidationError)
    async def request_validation_error(request, exc):
        error_msg = str(exc)
        Log.error(f"request validation error: {error_msg}")
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content=HttpResponse.failure(HTTP_422_UNPROCESSABLE_ENTITY, error_msg),
        )

    @application.exception_handler(BusinessException)
    async def business_error_handler(request, exc):
        Log.error(f"business error: {exc}")
        return JSONResponse(
            status_code=HTTP_200_OK,
            content=HttpResponse.failure(exc.code, exc.message),
        )

    @application.exception_handler(RpcException)
    async def rpc_error_handler(request, exc):
        error_msg = str(exc)
        Log.error(f"rpc error: {error_msg}")
        return JSONResponse(
            status_code=HTTP_200_OK,
            content=HttpResponse.failure(rpc_error_code, error_msg),
        )

    @application.exception_handler(Exception)
    async def custom_error_handler(request, exc):
        error_msg = str(exc)
        Log.error(f"custom error: {error_msg}")
        return JSONResponse(
            status_code=HTTP_200_OK,
            content=HttpResponse.failure(server_error_code, error_msg),
        )

    @application.get("/")
    async def home():
        return RedirectResponse(url="/docs")
