from test.api import api
from test.model.test import TestBody, TestCookies, TestHeaders, TestQuery, TestResp

from flask import Blueprint

from clio import (
    HttpResponse,
    Log,
    Request,
    Response,
    body,
    cookies,
    headers,
    logger,
    query,
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
def test_api():
    """测试接口
    eeee
    """
    q: TestQuery = query()
    Log.info(q)

    h = headers()
    Log.info(h)

    c = cookies()
    Log.info(c)

    b = body()
    Log.info(b)

    resp = TestResp(e="e")
    return HttpResponse.success(resp)
