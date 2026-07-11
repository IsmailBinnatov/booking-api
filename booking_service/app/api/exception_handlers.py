from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.exceptions.base import AppError
from app.exceptions.booking import (
    BookingNotFoundError,
    BookingCannotBePaidError,
    PaidBookingCannotBeCancelledError,
)
from app.exceptions.integrations import (
    FlightServiceUnavailableError,
    FlightServiceOperationError,
)


ERROR_STATUS_MAP: dict[type[AppError], int] = {
    BookingNotFoundError: status.HTTP_404_NOT_FOUND,
    BookingCannotBePaidError: status.HTTP_409_CONFLICT,
    PaidBookingCannotBeCancelledError: status.HTTP_409_CONFLICT,
    FlightServiceUnavailableError: status.HTTP_503_SERVICE_UNAVAILABLE,
    FlightServiceOperationError: status.HTTP_409_CONFLICT,
}


async def app_error_handler(
    request: Request,
    exc: AppError,
) -> JSONResponse:

    status_code = ERROR_STATUS_MAP.get(
        type(exc),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

    return JSONResponse(
        status_code=status_code,
        content={
            'error': {
                'code': exc.code,
                'message': exc.message,
            }
        },
    )
