from test.model.test import TestBody, TestResp

from fastapi import APIRouter

from clio import HttpResponse, Log, request

test_api_router = APIRouter(prefix="/test")


@test_api_router.post("/test")
async def test_api(test_body: TestBody):
    await test()
    resp = TestResp(e="e")
    Log.info("TEST")
    return HttpResponse.success(resp)


async def test():
    req = request()
    url = req.url
    Log.debug(f"test: {url}")
