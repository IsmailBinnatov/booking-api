from app.exceptions.base import AppError


# class FlightNotFoundError(AppError):
#     ...


class SeatsUnavailableError(AppError):
    code = 'seats_unavailable'

    def __init__(
        self,
        flight_id,
    ) -> None:
        self.flight_id = flight_id
        super().__init__(
            message=f'Some seats on flight ID: {flight_id} are unavailable'
        )


class SeatsCannotBeBookedError(AppError):
    code = 'seats_cannot_be_booked'

    def __init__(
        self,
        flight_id,
    ) -> None:
        self.flight_id = flight_id
        super().__init__(
            message=f'Some or all seats cannot be booked on flight ID: {flight_id}'
        )


class SeatsCannotBeUnlockedError(AppError):
    code = 'seats_cannot_be_unlocked'

    def __init__(
        self,
        flight_id,
    ) -> None:
        self.flight_id = flight_id
        super().__init__(
            message=f'Some seats on flight ID: {flight_id} could not be unlocked'
        )
