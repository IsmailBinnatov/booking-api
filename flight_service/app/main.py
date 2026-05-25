from fastapi import FastAPI

from app.api.routers.v1.flights import router as flights_router
from app.api.routers.v1.internal_flights import router as internal_flights_router


app = FastAPI(
    title="AirSales Flight Service",
    description="Microservice for searching and booking flights",
    version="1.0.0",
)


app.include_router(flights_router, prefix='/api/v1')
app.include_router(internal_flights_router, prefix='/api/v1')
