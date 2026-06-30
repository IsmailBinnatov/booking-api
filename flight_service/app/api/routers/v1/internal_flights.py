from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.services.flight_service import FlightService
from app.schemas.flight import BookSeatsRequest


router = APIRouter(
    prefix='/internal/flights',
    tags=['Internal Flights'],
)


@router.post(
    '/{flight_id}/seats/lock',
    status_code=status.HTTP_200_OK,
)
async def lock_seat(
    flight_id: int,
    booking_data: BookSeatsRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    An endpoint for temporarily reserving a seat for 10 minutes.
    Called by the Booking Service when the order process begins.
    """
    return await FlightService.lock_seats_for_booking(
        db=db,
        flight_id=flight_id,
        seat_numbers=booking_data.seat_numbers,
    )


@router.post(
    '/{flight_id}/seats/book',
    status_code=status.HTTP_200_OK,
)
async def confirm_seat_booking(
    flight_id: int,
    booking_data: BookSeatsRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint for final seat confirmation.
    Called by the Booking Service immediately after successful payment.
    """
    return await FlightService.confirm_seats_booking(
        db=db,
        flight_id=flight_id,
        seat_numbers=booking_data.seat_numbers,
    )


@router.post(
    '/{flight_id}/seats/unlock',
    status_code=status.HTTP_200_OK,
)
async def unlock_locked_seats(
    flight_id: int,
    booking_data: BookSeatsRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint for cancelling seat booking.
    Called by the Booking Service for unlocking seat.
    """
    return await FlightService.unlock_locked_seats(
        db=db,
        flight_id=flight_id,
        seat_numbers=booking_data.seat_numbers,
    )
