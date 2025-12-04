"""Theater and Hall models."""

from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import Theaterowner
    from .screening import Screening
    from .booking import Booking


class Theater(Base):
    __tablename__ = 'theater'
    __table_args__ = (
        ForeignKeyConstraint(['ownerid'], ['theaterowner.id'], name='theater_ownerid_fkey'),
        PrimaryKeyConstraint('companyid', 'branchid', name='theater_pkey')
    )

    companyid: Mapped[str] = mapped_column(String(50), primary_key=True)
    branchid: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    ownerid: Mapped[int] = mapped_column(Integer, nullable=False)
    contact: Mapped[Optional[str]] = mapped_column(String(20))
    logourl: Mapped[Optional[str]] = mapped_column(String(255))
    isverified: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))

    theaterowner: Mapped['Theaterowner'] = relationship('Theaterowner', back_populates='theater')
    hall: Mapped[list['Hall']] = relationship('Hall', back_populates='theater')


class Hall(Base):
    __tablename__ = 'hall'
    __table_args__ = (
        ForeignKeyConstraint(['companyid', 'branchid'], ['theater.companyid', 'theater.branchid'], name='hall_companyid_branchid_fkey'),
        PrimaryKeyConstraint('hallid', 'companyid', 'branchid', name='hall_pkey')
    )

    hallid: Mapped[str] = mapped_column(String(50), primary_key=True)
    companyid: Mapped[str] = mapped_column(String(50), primary_key=True)
    branchid: Mapped[str] = mapped_column(String(50), primary_key=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    theater: Mapped['Theater'] = relationship('Theater', back_populates='hall')
    screening: Mapped[list['Screening']] = relationship('Screening', back_populates='hall')


class Seatlayout(Hall):
    __tablename__ = 'seatlayout'
    __table_args__ = (
        ForeignKeyConstraint(['layouthallid', 'layoutcompanyid', 'layoutbranchid'], ['hall.hallid', 'hall.companyid', 'hall.branchid'], name='seatlayout_layouthallid_layoutcompanyid_layoutbranchid_fkey'),
        PrimaryKeyConstraint('layouthallid', 'layoutcompanyid', 'layoutbranchid', name='seatlayout_pkey')
    )

    layouthallid: Mapped[str] = mapped_column(String(50), primary_key=True)
    layoutcompanyid: Mapped[str] = mapped_column(String(50), primary_key=True)
    layoutbranchid: Mapped[str] = mapped_column(String(50), primary_key=True)

    seat: Mapped[list['Seat']] = relationship('Seat', back_populates='seatlayout')


class Seat(Base):
    __tablename__ = 'seat'
    __table_args__ = (
        ForeignKeyConstraint(['layouthallid', 'layoutcompanyid', 'layoutbranchid'], ['seatlayout.layouthallid', 'seatlayout.layoutcompanyid', 'seatlayout.layoutbranchid'], name='seat_layouthallid_layoutcompanyid_layoutbranchid_fkey'),
        PrimaryKeyConstraint('seatid', 'layouthallid', 'layoutcompanyid', 'layoutbranchid', name='seat_pkey')
    )

    seatid: Mapped[str] = mapped_column(String(50), primary_key=True)
    layouthallid: Mapped[str] = mapped_column(String(50), primary_key=True)
    layoutcompanyid: Mapped[str] = mapped_column(String(50), primary_key=True)
    layoutbranchid: Mapped[str] = mapped_column(String(50), primary_key=True)
    rownumber: Mapped[str] = mapped_column(String(10), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'AVAILABLE'::character varying"))

    booking: Mapped[list['Booking']] = relationship('Booking', secondary='bookingseat', back_populates='seat')
    seatlayout: Mapped['Seatlayout'] = relationship('Seatlayout', back_populates='seat')