import httpx

from fastapi import HTTPException

from app.repositories.booking_repo import BookingRepository
from app.models.models import Booking, BookingStatus


class BookingService:
    def __init__(
        self,
        booking_repo: BookingRepository,
        flight_client: httpx.AsyncClient,
    ):
        self.booking_repo = booking_repo
        self.flight_client = flight_client

    async def create_booking(
        self,
        user_id: int,
        flight_id: int,
        seat_numbers: list[str],
    ) -> Booking:

        await self.flight_service_lock_seats(
            flight_id=flight_id,
            seat_numbers=seat_numbers,
        )

        booking = await self.booking_repo.create_booking(
            user_id=user_id,
            flight_id=flight_id,
            seat_numbers=seat_numbers,
        )

        return booking

    async def get_booking_by_id(
        self,
        user_id: int,
        booking_id: int,
    ) -> Booking | None:

        booking = await self.booking_repo.get_current_user_booking_by_id(
            user_id=user_id,
            booking_id=booking_id,
        )
        return booking

    async def update_booking_status(
        self,
        booking_id: int,
        new_status: BookingStatus,
    ) -> bool:

        update_booking = await self.booking_repo.update_booking_status(
            booking_id=booking_id,
            new_status=new_status,
        )

        return update_booking

    async def flight_service_lock_seats(
        self,
        flight_id: int,
        seat_numbers: list[str],
    ) -> None:

        try:
            response = await self.flight_client.post(
                url=f'/api/v1/internal/flights/{flight_id}/seats/lock',
                json={
                    'seat_numbers': seat_numbers,
                },
            )
            response.raise_for_status()

        except httpx.HTTPStatusError as exc:
            error_data = exc.response.json()

            raise HTTPException(
                status_code=exc.response.status_code,
                detail=error_data.get(
                    'detail',
                    'Flight Service could not lock the requested seats',
                ),
            )

        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail='Flight Service is currently unavailable',
            )

    async def flight_service_book_seats(
        self,
        user_id: int,
        booking_id: int,
    ) -> None:

        booking = await self.booking_repo.get_current_user_booking_by_id(
            user_id=user_id,
            booking_id=booking_id,
        )

        # temporary
        if not booking:
            raise HTTPException(
                status_code=404,
                detail=f'you have not booking ID: {booking_id}'
            )

        if booking.status != BookingStatus.PENDING:
            raise HTTPException(
                status_code=403,
                detail='The booking already paid or cancelled'
            )

        seat_numbers = [
            seat.seat_number
            for seat in booking.booking_seats
        ]

        try:
            response = await self.flight_client.post(
                url=f'/api/v1/internal/flights/{booking.flight_id}/seats/book',
                json={
                    'seat_numbers': seat_numbers,
                },
            )
            response.raise_for_status()

            await self.booking_repo.update_booking_status(
                booking_id=booking.id,
                new_status=BookingStatus.PAID,
            )

        except httpx.HTTPStatusError as exc:
            error_data = exc.response.json()

            raise HTTPException(
                status_code=exc.response.status_code,
                detail=error_data.get(
                    'detail',
                    'Flight Service could not book the locked seats'
                )
            )

        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail='Flight Service is currently unavailable',
            )

    async def flight_service_cancel_booking(
        self,
        user_id: int,
        booking_id: int,
    ) -> None:

        booking = await self.booking_repo.get_current_user_booking_by_id(
            user_id=user_id,
            booking_id=booking_id,
        )

        if not booking:
            raise HTTPException(
                status_code=404,
                detail=f'You have not booking ID: {booking_id}'
            )

        if booking.status == BookingStatus.PAID:
            raise HTTPException(
                status_code=409,
                detail='Paid booking cannot be cancelled',
            )
        elif booking.status == BookingStatus.CANCELLED:
            return

        seat_numbers = [
            seat.seat_number
            for seat in booking.booking_seats
        ]

        try:
            response = await self.flight_client.post(
                f'/api/v1/internal/flights/{booking.flight_id}/seats/unlock',
                json={
                    'seat_numbers': seat_numbers,
                },
            )
            response.raise_for_status()

            await self.booking_repo.update_booking_status(
                booking_id=booking.id,
                new_status=BookingStatus.CANCELLED,
            )

        except httpx.HTTPStatusError as exc:
            error_data = exc.response.json()

            raise HTTPException(
                status_code=exc.response.status_code,
                detail=error_data.get(
                    'detail',
                    'Flight Service could not unlock the locked seats',
                )
            )

        except httpx.RequestError:
            raise HTTPException(
                status_code=503,
                detail='Flight Service is currently unavailable',
            )
