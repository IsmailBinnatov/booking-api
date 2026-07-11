from app.exceptions.base import AppError


class FlightServiceUnavailableError(AppError):
    code = 'flight_service_unavailable'

    def __init__(self) -> None:
        super().__init__(
            message='Flight Service is currently unavailable'
        )


class FlightServiceOperationError(AppError):
    code = 'flight_service_operation_error'

    def __init__(
        self,
        action: str,
        detail: str,
    ) -> None:
        self.action = action
        self.detail = detail

        super().__init__(
            message=(
                f'Flight Service operation \'{action}\' failed: {detail}'
            )
        )
