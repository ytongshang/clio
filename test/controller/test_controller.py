from test.api import api
from test.database import Members, db
from test.model.test import TestBody, TestCookies, TestHeaders, TestQuery, TestResp

from quart import Blueprint

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
    return HttpResponse.success(resp)


@test_bp.route("/test1", methods=["GET"])
@logger
async def test_api2():
    print("test_api2")
    users = db.session.query(Members).all()
    print(users)
    return HttpResponse.success(1)
