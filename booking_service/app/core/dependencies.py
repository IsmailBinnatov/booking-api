import httpx
from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.repositories.booking_repo import BookingRepository
from app.services.booking_service import BookingService


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


async def get_booking_repo(
    db: AsyncSession = Depends(get_db)
) -> BookingRepository:
    return BookingRepository(db=db)


async def get_booking_service(
    booking_repo: BookingRepository = Depends(get_booking_repo),
    flight_client: httpx.AsyncClient = Depends(get_flight_client),
) -> BookingService:
    return BookingService(
        booking_repo=booking_repo,
        flight_client=flight_client,
    )
