from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Flight
from app.schemas.flight import FlightQueryParams


class FlightRepository:
    @staticmethod
    async def get_all_flights(
        db: AsyncSession,
        filters: FlightQueryParams,
        limit: int = 10,
        offset: int = 0,
    ) -> Sequence[Flight]:

        query = select(Flight).options(selectinload(Flight.seats))
        if filters.departure_from:
            query = query.where(Flight.departure_from ==
                                filters.departure_from)
        if filters.arrival_to:
            query = query.where(Flight.arrival_to ==
                                filters.arrival_to)

        query = query.limit(limit).offset(offset)

        result = (await db.scalars(query)).all()
        return result
