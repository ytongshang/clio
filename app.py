import asyncio
from test.controller.test_controller import test_api_router

from fastapi import FastAPI
from hypercorn import Config
from hypercorn.asyncio import serve

from clio import exception_handler, hack_json
from clio.utils.log import console_handler, default_logger
from clio.web.context.middleware import RawContextMiddleware

hack_json()
console_handler(default_logger)

app = FastAPI()
exception_handler(app)

# 添加 CORS 中间件
app.add_middleware(
    RawContextMiddleware,
)
app.include_router(test_api_router)

if __name__ == "__main__":
    config = Config.from_pyfile("hypercorn.conf.py")
    config.use_reloader = True
    asyncio.run(serve(app, config))
