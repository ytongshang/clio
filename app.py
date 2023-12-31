import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from clio import SessionMiddleware, common_exception_handlers
from clio.web.context.middleware import RawContextMiddleware
from example.controller.test_controller import test_api_router
from example.database.database import db


def create_app():
    # database
    init_database()

    application = FastAPI(
        exception_handlers=common_exception_handlers(),
    )
    # middlewares,后加的先执行
    application.add_middleware(SessionMiddleware, sqlalchemy=db)
    application.add_middleware(RawContextMiddleware)

    # routers
    application.include_router(test_api_router)

    @application.get("/")
    async def home():
        return RedirectResponse(url="/docs")

    return application


def init_database():
    from example.database import models  # noqa

    db.create_all()


app = create_app()

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
