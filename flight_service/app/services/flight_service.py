import json
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.flight_repository import FlightRepository
from app.repositories.seat_repository import SeatRepository
from app.schemas.flight import FlightQueryParams, FlightResponse
from app.core.dependencies import redis_client


class FlightService:

    @classmethod
    async def get_flights(
        cls,
        db: AsyncSession,
        filters: FlightQueryParams,
        limit: int = 10,
        offset: int = 0,
    ) -> list[dict[str, Any]]:

        cache_key = f'flights:{filters.departure_from}:{filters.arrival_to}:lim_{limit}:off_{offset}'
        cached_flights = await redis_client.get(cache_key)
        if cached_flights:
            print('--- [CACHE HIT] The data is taken from Redis ---')
            return json.loads(cached_flights)

        print('--- [CACHE MISS] Redis is empty. Going to PostgreSQL ---')
        db_flights = await FlightRepository.get_all_flights(
            db=db, filters=filters, limit=limit, offset=offset,
        )

        validated_flights = [FlightResponse.model_validate(f)
                             .model_dump(mode='json') for f in db_flights]
        await redis_client.set(cache_key, json.dumps(validated_flights), ex=300)
        return validated_flights

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
