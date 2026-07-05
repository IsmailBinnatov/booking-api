import httpx
import asyncio

from app.core.celery_app import celery_app
from app.core.database import celery_async_session_maker
from app.core.config import settings
from app.repositories.booking_repo import BookingRepository
from app.services.booking_service import BookingService


async def _run_cancel_pending_booking(booking_id: int) -> None:
    async with celery_async_session_maker() as session:
        try:
            async with httpx.AsyncClient(base_url=settings.FLIGHT_SERVICE_URL) as flight_client:
                booking_repo = BookingRepository(session)
                booking_service = BookingService(
                    booking_repo,
                    flight_client,
                )
                await booking_service.cancel_if_pending(booking_id)
                await session.commit()
        except Exception:
            await session.rollback()
            raise


@celery_app.task(ignore_result=True)
def cancel_pending_booking(booking_id: int):
    asyncio.run(_run_cancel_pending_booking(booking_id))
