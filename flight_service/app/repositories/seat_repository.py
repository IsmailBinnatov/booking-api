from collections.abc import Sequence
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Seat


class SeatRepository:

    @staticmethod
    async def get_seats_by_ids_for_update(
        db: AsyncSession,
        seat_ids: list[int],
    ) -> Sequence[Seat]:

        query = (
            select(Seat)
            .where(Seat.id.in_(seat_ids))
            .with_for_update()
        )

        result = (await db.scalars(query)).all()
        return result

    @staticmethod
    async def update_seats(db: AsyncSession) -> None:
        await db.flush()

    @staticmethod
    async def lock_seat(
        db: AsyncSession,
        flight_id: int,
        seat_number: str,
    ) -> int:
        now = datetime.now(timezone.utc)
        unlock_time = now + timedelta(minutes=10)

        query = (
            update(Seat)
            .where(Seat.flight_id == flight_id)
            .where(Seat.seat_number == seat_number)
            .where(Seat.is_booked == False)
            .where(or_(Seat.locked_until == None, Seat.locked_until < now))
            .values(locked_until=unlock_time)
        )

        result = await db.execute(query)
        await db.flush()

        return result.rowcount

    @staticmethod
    async def confirm_booking_seat(
        db: AsyncSession,
        flight_id: int,
        seat_number: str,
    ) -> int:

        query = (
            update(Seat)
            .where(Seat.flight_id == flight_id)
            .where(Seat.seat_number == seat_number)
            .values(
                is_booked=True,
                locked_until=None,
            )
        )

        result = await db.execute(query)
        await db.flush()

        return result.rowcount
