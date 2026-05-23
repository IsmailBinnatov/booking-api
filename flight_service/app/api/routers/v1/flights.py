from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.flight import FlightQueryParams, FlightResponse, SeatResponse, BookSeatsRequest
from app.services.flight_service import FlightService
from app.core.dependencies import get_db


router = APIRouter(prefix='/flights', tags=['Flights'])


@router.get('/', response_model=list[FlightResponse])
async def get_all_flights(
    filters: FlightQueryParams = Depends(),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    flights = await FlightService.get_flights(
        db=db,
        filters=filters,
        limit=limit,
        offset=offset,
    )
    return flights


@router.post('/book', response_model=list[SeatResponse])
async def book_flight_seats(
    body: BookSeatsRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns seats new status
    """
    updated_seats = await FlightService.book_seats(db=db, seat_ids=body.seat_ids)
    return updated_seats
