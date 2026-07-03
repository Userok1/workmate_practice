from fastapi import FastAPI, Request
import uvicorn
from contextlib import asynccontextmanager
from redis.exceptions import ConnectionError
import logging
import time

from src.crud.router import router
from src.crud.utils import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Redis connecting...")
        await redis_client.ping()
        logger.info("Redis connected")
    except ConnectionError:
        logger.error("Redis connection error")
        raise

    yield

    # await redis_client.flushall()
    await redis_client.aclose()


app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/")
async def main():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
