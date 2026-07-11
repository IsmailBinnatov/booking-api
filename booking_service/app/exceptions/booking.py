from app.exceptions.base import AppError
from app.models.models import BookingStatus


class BookingNotFoundError(AppError):
    code = 'booking_not_found'

    def __init__(
        self,
        booking_id: int,
    ) -> None:
        self.booking_id = booking_id
        super().__init__(
            message=f'Booking ID: {booking_id} not found'
        )


class BookingCannotBePaidError(AppError):
    code = 'booking_cannot_be_paid'

    def __init__(
        self,
        booking_id: int,
        current_status: BookingStatus,
    ) -> None:
        self.booking_id = booking_id
        self.current_status = current_status

        super().__init__(
            message=(
                f'Booking ID: {booking_id} cannot be paid, \
                    because current status is {current_status.value}'
            )
        )


class PaidBookingCannotBeCancelledError(AppError):
    code = 'paid_booking_cannot_be_cancelled'

    def __init__(
        self,
        booking_id: int,
    ) -> None:
        self.booking_id = booking_id
        super().__init__(
            message=(
                f'Booking ID: {booking_id} cannot be cancelled'
                f'because it has already been paid'
            )
        )
