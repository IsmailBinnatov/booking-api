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
    async def _clear_flights_cache() -> None:
        """
        Asynchronously finds and deletes all cache keys that begin with the prefix 'flights:'
        """
        try:
            async for key in redis_client.scan_iter(match='flights:*'):
                await redis_client.delete(key)
        except Exception as e:
            print(f'--- [CACHE ERROR] Failed to clear cache: {e} ---')

    @staticmethod
    async def lock_seat_for_booking(
        db: AsyncSession,
        flight_id: int,
        seat_number: str,
    ) -> dict[str, str]:

        updated_rows = await SeatRepository.lock_seat(
            db=db,
            flight_id=flight_id,
            seat_number=seat_number,
        )

        if updated_rows == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Seat {seat_number} on flight {flight_id} has already been booked or reserved by another user',
            )

        await FlightService._clear_flights_cache()

        return {
            'status': 'success',
            'message': f'Seat {seat_number} has been successfully reserved for 10 minutes',
        }

    @staticmethod
    async def confirm_seat_booking(
        db: AsyncSession,
        flight_id: int,
        seat_number: str,
    ) -> dict[str, str]:
        """
        Business logic for confirming seat reservation after successful payment.
        """
        updated_rows = await SeatRepository.confirm_booking_seat(
            db=db,
            flight_id=flight_id,
            seat_number=seat_number,
        )

        if updated_rows == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Seat {seat_number} on flight \'{flight_id}\' not found in the system or already reserved',
            )

        await FlightService._clear_flights_cache()

        return {
            'status': 'success',
            'message': f'Seat {seat_number} on flight {flight_id} has been successfully booked permanently',
        }
