import asyncio
from test.app import app

from hypercorn import Config
from hypercorn.asyncio import serve

if __name__ == "__main__":
    config = Config()
    config.bind = ["localhost:8000"]
    asyncio.run(serve(app, config))
