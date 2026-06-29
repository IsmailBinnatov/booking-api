from fastapi import APIRouter, Depends, status, HTTPException

from app.schemas.schemas import BookingCreate, BookingResponse
from app.schemas.token import TokenPayload
from app.core.dependencies import get_booking_service
from app.core.auth.auth_dependencies import get_current_token_payload
from app.services.booking_service import BookingService


router = APIRouter(
    prefix='/bookings',
    tags=['Booking Service'],
)


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    flight_data: BookingCreate,
    payload: TokenPayload = Depends(get_current_token_payload),
    booking_service: BookingService = Depends(get_booking_service),
) -> dict[str, str]:

    booking = await booking_service.create_booking(
        user_id=payload.user_id,
        flight_id=flight_data.flight_id,
        seat_numbers=flight_data.seat_numbers,
    )

    return {
        'message': f'Booking ID: {booking.id} successfully created'
    }


@router.post(
    '/{booking_id}/pay',
    status_code=status.HTTP_200_OK,
)
async def pay_and_confirm_booking(
    booking_id: int,
    payload: TokenPayload = Depends(get_current_token_payload),
    booking_service: BookingService = Depends(get_booking_service),
) -> dict[str, str]:

    await booking_service.flight_service_book_seats(
        user_id=payload.user_id,
        booking_id=booking_id,
    )

    return {
        'message': f'Booking ID: {booking_id} successfully paid'
    }


@router.get(
    '/{booking_id}',
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
)
async def get_booking_by_id(
    booking_id: int,
    payload: TokenPayload = Depends(get_current_token_payload),
    booking_service: BookingService = Depends(get_booking_service),
) -> BookingResponse:

    booking = await booking_service.get_booking_by_id(
        user_id=payload.user_id,
        booking_id=booking_id,
    )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Booking not found',
        )

    return booking
