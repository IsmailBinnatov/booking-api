from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.flight_repository import FlightRepository
from app.repositories.seat_repository import SeatRepository
from app.schemas.flight import FlightQueryParams


class FlightService:

    @staticmethod
    async def get_flights(
        db: AsyncSession,
        filters: FlightQueryParams,
        limit: int = 10,
        offset: int = 0,
    ):
        return await FlightRepository.get_all_flights(
            db, filters, limit, offset,
        )

    @staticmethod
    async def book_seats(
        db: AsyncSession,
        seat_ids: list[int],
    ):
        seats = await SeatRepository.get_seats_by_ids_for_update(db, seat_ids)

        if len(seats) != len(seat_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Seat or seats are not found'
            )

        for seat in seats:
            if seat.is_booked:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'The seat {seat.seat_number} is already booked'
                )

            seat.is_booked = True

        await SeatRepository.update_seats(db)
        return seats
