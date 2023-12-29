import asyncio

from fastapi import FastAPI
from hypercorn import Config
from hypercorn.asyncio import serve

from clio import SessionMiddleware, register_exception_handler
from clio.web.context.middleware import RawContextMiddleware
from example.controller.test_controller import test_api_router
from example.database.database import db


def create_app():
    application = FastAPI()
    register_exception_handler(application)

    application.include_router(test_api_router)

    # database
    init_database(application)

    application.add_middleware(
        RawContextMiddleware,
    )
    return application


def init_database(application: FastAPI = None):
    from example.database import entity  # noqa

    application.add_middleware(SessionMiddleware, sqlalchemy=db)
    db.create_all()


app = create_app()

if __name__ == "__main__":
    config = Config.from_pyfile("hypercorn.conf.py")
    config.use_reloader = True
    config.workers = 1
    asyncio.run(serve(app, config))
