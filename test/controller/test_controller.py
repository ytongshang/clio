import asyncio
from test.api import api
from test.model.test import TestBody, TestCookies, TestHeaders, TestQuery, TestResp

from flask import Blueprint

from clio import (
    HttpResponse,
    Log,
    Request,
    Response,
    http_body,
    http_cookies,
    http_headers,
    http_query,
    logger,
)

test_bp = Blueprint("test_bp", __name__, url_prefix="/test")


@test_bp.route("/test", methods=["POST"])
@api.validate(
    query=TestQuery,
    cookies=TestCookies,
    headers=TestHeaders,
    body=Request(TestBody),
    resp=Response(HTTP_200=HttpResponse[TestResp]),
)
@logger
async def test_api():
    """测试接口
    eeee
    """
    q: TestQuery = http_query()
    Log.info(q)

    h: TestHeaders = http_headers()
    Log.info(h)

    c: TestCookies = http_cookies()
    Log.info(c)

    b: TestBody = http_body()
    Log.info(b)

    resp = TestResp(e="e")
    Log.info("TEST")
    await asyncio.sleep(1000000)
    return HttpResponse.success(resp)


@test_bp.route("/test1", methods=["GET"])
@logger
async def test_api2():
    print("test_api2")
    await asyncio.sleep(1000000)
    return HttpResponse.success(1)
