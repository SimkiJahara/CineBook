"""Promocode model."""

import datetime
import decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKeyConstraint, Integer, Numeric, PrimaryKeyConstraint, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import Superadmin
    from .booking import Booking


class Promocode(Base):
    __tablename__ = 'promocode'
    __table_args__ = (
        ForeignKeyConstraint(['createdbyadminid'], ['superadmin.id'], name='promocode_createdbyadminid_fkey'),
        PrimaryKeyConstraint('code', name='promocode_pkey')
    )

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    discountvalue: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    discounttype: Mapped[str] = mapped_column(String(50), nullable=False)
    validfrom: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    validto: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    applied_to: Mapped[decimal.Decimal] = mapped_column(Numeric(3, 2), nullable=False, server_default=text('1.0'))
    createdbyadminid: Mapped[int] = mapped_column(Integer, nullable=False)
    maxuses: Mapped[Optional[int]] = mapped_column(Integer)
    currentusecount: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    scope: Mapped[Optional[str]] = mapped_column(String(50))

    superadmin: Mapped['Superadmin'] = relationship('Superadmin', back_populates='promocode')
    booking: Mapped[list['Booking']] = relationship('Booking', back_populates='promocode_')