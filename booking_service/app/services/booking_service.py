import httpx

from app.repositories.booking_repo import BookingRepository
from app.models.models import Booking, BookingStatus
from app.exceptions.booking import (
    BookingNotFoundError,
    BookingCannotBePaidError,
    PaidBookingCannotBeCancelledError,
)
from app.exceptions.integrations import (
    FlightServiceUnavailableError,
    FlightServiceOperationError,
)


class BookingService:
    def __init__(
        self,
        booking_repo: BookingRepository,
        flight_client: httpx.AsyncClient,
    ):
        self.booking_repo = booking_repo
        self.flight_client = flight_client

    def _get_seat_numbers(
        self,
        booking: Booking,
    ) -> list[str]:

        return [seat.seat_number for seat in booking.booking_seats]

    async def create_booking(
        self,
        user_id: int,
        flight_id: int,
        seat_numbers: list[str],
    ) -> Booking:

        from app.tasks.booking_tasks import cancel_pending_booking

        await self.flight_service_lock_seats(
            flight_id=flight_id,
            seat_numbers=seat_numbers,
        )

        try:
            booking = await self.booking_repo.create_booking(
                user_id=user_id,
                flight_id=flight_id,
                seat_numbers=seat_numbers,
            )

            cancel_pending_booking.apply_async(
                args=[booking.id],
                countdown=605,
            )

            return booking
        except Exception:
            await self.flight_service_seats_request(
                flight_id=flight_id,
                seat_numbers=seat_numbers,
                url_action='unlock'
            )
            raise

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

    async def flight_service_seats_request(
        self,
        flight_id: int,
        seat_numbers: list[str],
        url_action: str,
    ) -> None:

        try:
            response = await self.flight_client.post(
                url=f'/api/v1/internal/flights/{flight_id}/seats/{url_action}',
                json={
                    'seat_numbers': seat_numbers,
                },
            )
            response.raise_for_status()

        except httpx.HTTPStatusError as exc:
            error_data = exc.response.json()

            raise FlightServiceOperationError(
                url_action,
                detail=error_data.get(
                    'detail',
                    'Flight Service could not process seats request',
                ),
            )

        except httpx.RequestError:
            raise FlightServiceUnavailableError()

    async def flight_service_lock_seats(
        self,
        flight_id: int,
        seat_numbers: list[str],
    ) -> None:

        await self.flight_service_seats_request(
            flight_id=flight_id,
            seat_numbers=seat_numbers,
            url_action='lock',
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

        if not booking:
            raise BookingNotFoundError(booking_id)

        if booking.status != BookingStatus.PENDING:
            raise BookingCannotBePaidError(
                booking.id,
                booking.status,
            )

        await self.flight_service_seats_request(
            flight_id=booking.flight_id,
            seat_numbers=self._get_seat_numbers(booking),
            url_action='book',
        )

        await self.booking_repo.update_booking_status(
            booking_id=booking.id,
            new_status=BookingStatus.PAID,
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
            raise BookingNotFoundError(booking_id)

        if booking.status == BookingStatus.PAID:
            raise PaidBookingCannotBeCancelledError(booking_id)
        elif booking.status == BookingStatus.CANCELLED:
            return

        await self.flight_service_seats_request(
            flight_id=booking.flight_id,
            seat_numbers=self._get_seat_numbers(booking),
            url_action='unlock',
        )

        await self.booking_repo.update_booking_status(
            booking_id=booking.id,
            new_status=BookingStatus.CANCELLED,
        )

    async def cancel_if_pending(
        self,
        booking_id: int,
    ) -> None:

        booking = await self.booking_repo.get_booking_by_id(booking_id)

        if not booking or booking.status != BookingStatus.PENDING:
            return None

        await self.flight_service_seats_request(
            flight_id=booking.flight_id,
            seat_numbers=self._get_seat_numbers(booking),
            url_action='unlock',
        )

        await self.update_booking_status(
            booking_id=booking.id,
            new_status=BookingStatus.CANCELLED,
        )
