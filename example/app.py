import asyncio

from fastapi import FastAPI
from hypercorn import Config
from hypercorn.asyncio import serve
from starlette.middleware import Middleware
from starlette.responses import RedirectResponse

from clio import SessionMiddleware, common_exception_handlers
from clio.web.context.middleware import RawContextMiddleware
from example.controller.test_controller import test_api_router
from example.database.database import db


def create_app():
    # database
    init_database()

    # exception handlers
    exception_handlers = common_exception_handlers()

    # middlewares
    middlewares = [
        Middleware(RawContextMiddleware),
        Middleware(
            SessionMiddleware,
            sqlalchemy=db,
        ),
    ]

    application = FastAPI(
        exception_handlers=exception_handlers, middlewares=middlewares
    )

    # routers
    application.include_router(test_api_router)

    @application.get("/")
    async def home():
        return RedirectResponse(url="/docs")

    return application


def init_database():
    from example.database import entity  # noqa

    db.create_all()


app = create_app()

if __name__ == "__main__":
    config = Config.from_pyfile("hypercorn.conf.py")
    config.use_reloader = True
    config.workers = 1
    asyncio.run(serve(app, config))
