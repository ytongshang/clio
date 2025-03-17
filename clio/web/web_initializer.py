from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from ..logger import Log
from .exception.business_exception import BusinessException
from .exception.rpc_exception import RpcException
from .http_response import HttpResponse


def common_exception_handlers(
    server_error_code: int = 500,
    rpc_error_code: int = 500,
):
    exception_handlers = {}

    async def not_found_error_handler(request, exc):
        url = request.url
        msg = f"404 not found: {url}"
        Log.error(msg, exc_info=False)
        return JSONResponse(
            status_code=HTTP_404_NOT_FOUND,
            content=HttpResponse.failure(HTTP_404_NOT_FOUND, msg),
        )

    exception_handlers[404] = not_found_error_handler

    async def request_validation_error(request, exc: RequestValidationError):
        error_msg = str(exc)
        Log.error(f"request validation error: {error_msg}")
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content=HttpResponse.failure(HTTP_422_UNPROCESSABLE_ENTITY, error_msg),
        )

    exception_handlers[RequestValidationError] = request_validation_error

    async def business_error_handler(request, exc: BusinessException):
        Log.error(f"business error: {exc}")
        return JSONResponse(
            status_code=HTTP_200_OK,
            content=HttpResponse.failure(exc.code, exc.message),
        )

    exception_handlers[BusinessException] = business_error_handler

    async def rpc_error_handler(request, exc: RpcException):
        error_msg = str(exc)
        Log.error(f"rpc error: {error_msg}")
        return JSONResponse(
            status_code=HTTP_200_OK,
            content=HttpResponse.failure(rpc_error_code, error_msg),
        )

    exception_handlers[RpcException] = rpc_error_handler

    async def custom_error_handler(request, exc: Exception):
        error_msg = str(exc)
        Log.error(f"custom error: {error_msg}", exc_info=False)
        return JSONResponse(
            status_code=HTTP_200_OK,
            content=HttpResponse.failure(server_error_code, error_msg),
        )

    exception_handlers[500] = custom_error_handler
    return exception_handlers
