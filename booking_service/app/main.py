import httpx
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core import dependencies
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    dependencies.flight_client = httpx.AsyncClient(
        base_url=settings.FLIGHT_SERVICE_URL
    )
    print('--- [LIFESPAN] HTTP Client has been opened ---')

    yield

    await dependencies.flight_client.aclose()
    print('--- [LIFESPAN] HTTP Client has been closed ---')


app = FastAPI(
    title='AirSales Booking Service',
    version='1.0.0',
    lifespan=lifespan,
)


@app.get('/')
async def root():
    return {'message: Booking Service is ready to communicate!'}
