import enum
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    func,
    UniqueConstraint,
)

from app.core.database import Base


class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class Booking(Base):
    __tablename__ = 'bookings'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    flight_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus),
        default=BookingStatus.PENDING,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    booking_seats: Mapped[list['BookingSeat']] = relationship(
        back_populates='booking',
        cascade='all, delete-orphan',
    )


class BookingSeat(Base):
    __tablename__ = 'booking_seats'
    __table_args__ = (
        UniqueConstraint(
            'booking_id',
            'seat_number',
            name='uq_booking_seats_booking_id_seat_number',
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(
        ForeignKey(
            'bookings.id',
            ondelete='CASCADE',
        )
    )
    seat_number: Mapped[str] = mapped_column(String(5))

    booking: Mapped['Booking'] = relationship(
        back_populates='booking_seats',
    )
