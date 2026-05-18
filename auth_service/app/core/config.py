from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # DB
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_NAME: str
    DB_PORT: int

    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    # Redis limiter
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    @property
    def database_url(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    @property
    def redis_url(self) -> str:
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}'


settings = Settings()
