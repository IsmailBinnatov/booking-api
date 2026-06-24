import httpx
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker


flight_client: httpx.AsyncClient | None = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_flight_client() -> httpx.AsyncClient:
    if flight_client is None:
        raise RuntimeError("HTTP client is not initialized!")
    return flight_client
