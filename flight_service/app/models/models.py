from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Flight(Base):
    __tablename__ = 'flights'

    id: Mapped[int] = mapped_column(primary_key=True)
    flight_number: Mapped[str] = mapped_column(String(10), index=True)
    departure_from: Mapped[str] = mapped_column(String(4))
    arrival_to: Mapped[str] = mapped_column(String(4))
    departure_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    arrival_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    seats: Mapped[list['Seat']] = relationship(
        'Seat',
        cascade='all, delete-orphan',
        back_populates='flight',
    )


class Seat(Base):
    __tablename__ = 'seats'

    id: Mapped[int] = mapped_column(primary_key=True)
    flight_id: Mapped[int] = mapped_column(
        ForeignKey('flights.id', ondelete='CASCADE'),
        index=True,
    )
    seat_number: Mapped[str] = mapped_column(String(5))
    is_booked: Mapped[bool] = mapped_column(Boolean, default=False)
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    flight: Mapped['Flight'] = relationship(
        'Flight',
        back_populates='seats',
    )
