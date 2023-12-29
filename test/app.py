from fastapi import FastAPI

from clio import hack_json
from clio.web.context.middleware import RawContextMiddleware

hack_json()

app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    RawContextMiddleware,
)
