from datetime import datetime, timedelta, timezone

from sqlalchemy import update, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Seat


class SeatRepository:

    @staticmethod
    async def lock_seats(
        db: AsyncSession,
        flight_id: int,
        seat_numbers: list[str],
    ) -> int:
        now = datetime.now(timezone.utc)
        unlock_time = now + timedelta(minutes=10)

        query = (
            update(Seat)
            .where(Seat.flight_id == flight_id)
            .where(Seat.seat_number.in_(seat_numbers))
            .where(Seat.is_booked.is_(False))
            .where(or_(
                Seat.locked_until.is_(None),
                Seat.locked_until < now)
            )
            .values(locked_until=unlock_time)
        )

        result = await db.execute(query)
        return result.rowcount

    @staticmethod
    async def book_seats(
        db: AsyncSession,
        flight_id: int,
        seat_numbers: list[str],
    ) -> int:
        now = datetime.now(timezone.utc)

        query = (
            update(Seat)
            .where(Seat.flight_id == flight_id)
            .where(Seat.seat_number.in_(seat_numbers))
            .where(Seat.is_booked.is_(False))
            .where(Seat.locked_until > now)
            .values(
                is_booked=True,
                locked_until=None,
            )
        )

        result = await db.execute(query)
        return result.rowcount

    @staticmethod
    async def unlock_seats(
        db: AsyncSession,
        flight_id: int,
        seat_numbers: list[str],
    ) -> int:
        query = (
            update(Seat)
            .where(Seat.flight_id == flight_id)
            .where(Seat.seat_number.in_(seat_numbers))
            .where(Seat.is_booked.is_(False))
            .values(
                locked_until=None,
            )
        )

        result = await db.execute(query)
        return result.rowcount
