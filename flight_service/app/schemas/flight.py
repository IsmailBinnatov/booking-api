from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class FlightQueryParams(BaseModel):
    departure_from: str | None = Field(None, max_length=4)
    arrival_to: str | None = Field(None, max_length=4)
    date: datetime | None = None


class SeatResponse(BaseModel):
    id: int
    seat_number: str
    is_booked: bool

    model_config = ConfigDict(from_attributes=True)


class FlightResponse(BaseModel):
    id: int
    flight_number: str
    departure_from: str
    arrival_to: str
    departure_time: datetime
    arrival_time: datetime
    price: Decimal
    seats: list[SeatResponse] = []

    model_config = ConfigDict(from_attributes=True)
