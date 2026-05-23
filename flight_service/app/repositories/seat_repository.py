from collections.abc import Sequence

from sqlalchemy import select
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
