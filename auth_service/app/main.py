from fastapi import FastAPI

from app.api.routers.auth import router as auth_router


app = FastAPI(
    title='AirSales - Auth Service',
    description='Authorization and user management microservice',
    version='1.0.0'
)

app.include_router(auth_router)


@app.get('/')
async def root():
    return {'message': 'The Auth Service is operating normally'}
