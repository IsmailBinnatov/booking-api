from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # DB
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_NAME: str
    DB_PORT: int

    # Flight Service
    FLIGHT_SERVICE_URL: str

    # JWT Secret Key
    SECRET_KEY: str
    ALGORITHM: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int

    model_config = SettingsConfigDict(
        env_file=('.env', '.env.local'),
        extra='ignore',
    )

    @property
    def database_url(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    @property
    def redis_broker_url(self):
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0'


settings = Settings()
