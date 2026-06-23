from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.models import BookingStatus


class BookingCreate(BaseModel):
    flight_id: int
    seat_numbers: list[str] = Field(min_length=1)


class BookingSeatResponse(BaseModel):
    id: int
    seat_number: str

    model_config = ConfigDict(from_attributes=True)


class BookingResponse(BaseModel):
    id: int
    user_id: int
    flight_id: int
    status: BookingStatus
    created_at: datetime
    booking_seats: list[BookingSeatResponse]

    model_config = ConfigDict(from_attributes=True)
