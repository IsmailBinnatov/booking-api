from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.exceptions.base import AppError
from app.exceptions.flight import (
    SeatsUnavailableError,
    SeatsCannotBeBookedError,
    SeatsCannotBeUnlockedError,
)


ERROR_STATUS_MAP: dict[type[AppError], int] = {
    SeatsUnavailableError: status.HTTP_409_CONFLICT,
    SeatsCannotBeBookedError: status.HTTP_400_BAD_REQUEST,
    SeatsCannotBeUnlockedError: status.HTTP_409_CONFLICT,
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
