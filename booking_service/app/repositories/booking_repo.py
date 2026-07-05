from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Booking, BookingSeat, BookingStatus


class BookingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def flush(self):
        await self.db.flush()

    async def create_booking(
        self,
        user_id: int,
        flight_id: int,
        seat_numbers: list[str],
    ) -> Booking:

        booking_seats = [
            BookingSeat(seat_number=seat) for seat in seat_numbers
        ]

        booking = Booking(
            user_id=user_id,
            flight_id=flight_id,
            booking_seats=booking_seats,
        )

        self.db.add(booking)
        await self.db.flush()
        return booking

    async def get_current_user_booking_by_id(
        self,
        user_id: int,
        booking_id: int,
    ) -> Booking | None:

        query = (
            select(Booking)
            .where(Booking.id == booking_id)
            .where(Booking.user_id == user_id)
            .options(selectinload(Booking.booking_seats))
        )

        booking = (await self.db.execute(query)).scalar_one_or_none()
        return booking

    async def get_booking_by_id(
        self,
        booking_id: int,
    ) -> Booking | None:

        query = (
            select(Booking)
            .where(Booking.id == booking_id)
            .options(selectinload(Booking.booking_seats))
        )

        booking = (await self.db.execute(query)).scalar_one_or_none()
        return booking

    async def update_booking_status(
        self,
        booking_id: int,
        new_status: BookingStatus,
    ) -> bool:

        query = (
            update(Booking)
            .where(Booking.id == booking_id)
            .values(status=new_status)
        )

        update_booking = await self.db.execute(query)
        return update_booking.rowcount == 1
