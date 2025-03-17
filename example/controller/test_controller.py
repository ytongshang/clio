from fastapi import APIRouter

from clio import HttpResponse, Log

test_api_router = APIRouter(prefix="/test")


@test_api_router.get("/test")
async def test():
    Log.info("test")
    return HttpResponse.success(True)
