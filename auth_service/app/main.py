from contextlib import asynccontextmanager

from fastapi import FastAPI
from pyrate_limiter import Duration, Limiter, Rate, RedisBucket
import redis.asyncio as redis

from app.api.routers.auth import router as auth_router
from app.core.dependencies import rate_limiter
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url(settings.redis_url)
    bucket = await RedisBucket.init(
        rates=[Rate(5, Duration.MINUTE)],
        redis=redis_client,
        bucket_key='redis-limiter:auth',
    )
    rate_limiter.limiter = Limiter(bucket)
    yield
    await redis_client.aclose()


app = FastAPI(
    title='AirSales - Auth Service',
    description='Authorization and user management microservice',
    version='1.0.0'
)

app.include_router(auth_router)


@app.get('/')
async def root():
    return {'message': 'The Auth Service is operating normally'}
