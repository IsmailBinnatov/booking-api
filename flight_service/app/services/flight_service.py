import json
from loguru import logger
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.flight_repository import FlightRepository
from app.repositories.seat_repository import SeatRepository
from app.schemas.flight import FlightQueryParams, FlightResponse
from app.core.dependencies import redis_client


class FlightService:

    @staticmethod
    async def get_flights(
        db: AsyncSession,
        filters: FlightQueryParams,
        limit: int = 10,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Return cached flights if exists, else return flights from db
        """
        cache_key = f'flights:{filters.departure_from}:{filters.arrival_to}:lim_{limit}:off_{offset}'
        cached_flights = await redis_client.get(cache_key)
        if cached_flights:
            logger.info('[CACHE HIT] The data is taken from Redis')
            return json.loads(cached_flights)

        logger.info('[CACHE MISS] Redis is empty. Going to PostgreSQL')
        db_flights = await FlightRepository.get_all_flights(
            db=db,
            filters=filters,
            limit=limit,
            offset=offset,
        )

        validated_flights = [FlightResponse.model_validate(f)
                             .model_dump(mode='json') for f in db_flights]
        await redis_client.set(cache_key, json.dumps(validated_flights), ex=300)
        return validated_flights

    @staticmethod
    async def _clear_flights_cache() -> None:
        """
        Asynchronously finds and deletes all cache keys that begin with the prefix 'flights:'
        """
        try:
            async for key in redis_client.scan_iter(match='flights:*'):
                await redis_client.delete(key)
        except Exception as e:
            logger.error(f'[CACHE ERROR] Failed to clear cache: {e}')

    @staticmethod
    async def lock_seats_for_booking(
        db: AsyncSession,
        flight_id: int,
        seat_numbers: list[str],
    ) -> dict[str, str]:

        updated_rows = await SeatRepository.lock_seats(
            db=db,
            flight_id=flight_id,
            seat_numbers=seat_numbers,
        )

        if updated_rows != len(seat_numbers):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Seats: {", ".join(seat_numbers)} on flight \'{flight_id}\' has already been booked or reserved by another user',
            )

        await FlightService._clear_flights_cache()

        return {
            'status': 'success',
            'message': f'Seat {", ".join(seat_numbers)} has been successfully reserved for 10 minutes',
        }

    @staticmethod
    async def confirm_seats_booking(
        db: AsyncSession,
        flight_id: int,
        seat_numbers: list[str],
    ) -> dict[str, str]:
        """
        Business logic for confirming seats reservation after successful payment
        """
        updated_rows = await SeatRepository.book_seats(
            db=db,
            flight_id=flight_id,
            seat_numbers=seat_numbers,
        )

        if updated_rows != len(seat_numbers):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'Some seats on flight \'{flight_id}\' are unavailable',
            )

        await FlightService._clear_flights_cache()

        return {
            'status': 'success',
            'message': f'Seats: {", ".join(seat_numbers)} on flight \'{flight_id}\' has been successfully booked permanently',
        }

    @staticmethod
    async def unlock_locked_seats(
        db: AsyncSession,
        flight_id: int,
        seat_numbers: list[str],
    ) -> dict[str, str]:
        """
        Unlcoks given seats.
        """
        updated_rows = await SeatRepository.unlock_seats(
            db=db,
            flight_id=flight_id,
            seat_numbers=seat_numbers,
        )

        if updated_rows != len(seat_numbers):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f'Some seats on flight \'{flight_id}\' could not be unlocked. '
                    'They may be permanently booked or not exist.'
                ),
            )

        await FlightService._clear_flights_cache()

        return {
            'status': 'success',
            'message': f'Seats: {", ".join(seat_numbers)} on flight \'{flight_id}\' have been successfully unlocked',
        }
