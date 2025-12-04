"""Booking model."""

import datetime
import decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, DateTime, ForeignKeyConstraint, Integer, Numeric, PrimaryKeyConstraint, String, Table, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import Buyer
    from .promocode import Promocode
    from .screening import Screening
    from .theater import Seat


class Booking(Base):
    __tablename__ = 'booking'
    __table_args__ = (
        ForeignKeyConstraint(['buyerid'], ['buyer.id'], name='booking_buyerid_fkey'),
        ForeignKeyConstraint(['promocode'], ['promocode.code'], name='booking_promocode_fkey'),
        ForeignKeyConstraint(['screeningid'], ['screening.id'], name='booking_screeningid_fkey'),
        PrimaryKeyConstraint('bookingid', name='booking_pkey')
    )

    bookingid: Mapped[int] = mapped_column(Integer, primary_key=True)
    totalamount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    paymentmethod: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'PENDING'::character varying"))
    buyerid: Mapped[int] = mapped_column(Integer, nullable=False)
    screeningid: Mapped[int] = mapped_column(Integer, nullable=False)
    qrcodeurl: Mapped[Optional[str]] = mapped_column(String(255))
    bookedat: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    promocode: Mapped[Optional[str]] = mapped_column(String(50))

    buyer: Mapped['Buyer'] = relationship('Buyer', back_populates='booking')
    promocode_: Mapped[Optional['Promocode']] = relationship('Promocode', back_populates='booking')
    screening: Mapped['Screening'] = relationship('Screening', back_populates='booking')
    seat: Mapped[list['Seat']] = relationship('Seat', secondary='bookingseat', back_populates='booking')


t_bookingseat = Table(
    'bookingseat', Base.metadata,
    Column('bookingid', Integer, primary_key=True),
    Column('seatid', String(50), primary_key=True),
    Column('seatlayouthallid', String(50), primary_key=True),
    Column('seatlayoutcompanyid', String(50), primary_key=True),
    Column('seatlayoutbranchid', String(50), primary_key=True),
    ForeignKeyConstraint(['bookingid'], ['booking.bookingid'], name='bookingseat_bookingid_fkey'),
    ForeignKeyConstraint(['seatid', 'seatlayouthallid', 'seatlayoutcompanyid', 'seatlayoutbranchid'], ['seat.seatid', 'seat.layouthallid', 'seat.layoutcompanyid', 'seat.layoutbranchid'], name='bookingseat_seatid_seatlayouthallid_seatlayoutcompanyid_se_fkey'),
    PrimaryKeyConstraint('bookingid', 'seatid', 'seatlayouthallid', 'seatlayoutcompanyid', 'seatlayoutbranchid', name='bookingseat_pkey')
)