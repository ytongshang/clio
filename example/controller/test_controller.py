from fastapi import APIRouter

from clio import HttpResponse
from clio.utils.log import Log
from example.model.test import TestBody, TestResp
from example.service.test_service import TestService

test_api_router = APIRouter(prefix="/test")


@test_api_router.post("/test")
async def test(test_body: TestBody):
    await test()
    Log.info(f"test_body: {test_body}")
    resp = TestResp(e="e")
    return HttpResponse.success(resp)


@test_api_router.get("/db")
async def test_db():
    resp = await TestService.get_all()
    return HttpResponse.success(resp)
