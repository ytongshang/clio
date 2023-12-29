from test.app import app
from test.model.test import TestBody, TestResp

from clio import HttpResponse, Log


@app.post("/")
async def test_api(body: TestBody):
    print(body)
    resp = TestResp(e="e")
    Log.info("TEST")
    return HttpResponse.success(resp)
