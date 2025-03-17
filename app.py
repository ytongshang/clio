import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from clio import common_exception_handlers
from clio.web.middleware.middleware import RawContextMiddleware
from example.controller.test_controller import test_api_router


def create_app():
    application = FastAPI(
        exception_handlers=common_exception_handlers(),
    )
    application.include_router(test_api_router)
    # middlewares,后加的先执行
    application.add_middleware(RawContextMiddleware)

    @application.get("/")
    async def home():
        return RedirectResponse(url="/docs")

    return application


app = create_app()

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
