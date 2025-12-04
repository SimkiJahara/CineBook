"""Screening model."""

import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Date, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Time, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .theater import Hall
    from .movie import Movie
    from .booking import Booking


class Screening(Base):
    __tablename__ = 'screening'
    __table_args__ = (
        ForeignKeyConstraint(['hallid', 'hallcompanyid', 'hallbranchid'], ['hall.hallid', 'hall.companyid', 'hall.branchid'], name='screening_hallid_hallcompanyid_hallbranchid_fkey'),
        ForeignKeyConstraint(['movieeidr'], ['movie.eidr'], name='screening_movieeidr_fkey'),
        PrimaryKeyConstraint('id', name='screening_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    starttime: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'SCHEDULED'::character varying"))
    movieeidr: Mapped[str] = mapped_column(String(50), nullable=False)
    hallid: Mapped[str] = mapped_column(String(50), nullable=False)
    hallcompanyid: Mapped[str] = mapped_column(String(50), nullable=False)
    hallbranchid: Mapped[str] = mapped_column(String(50), nullable=False)

    hall: Mapped['Hall'] = relationship('Hall', back_populates='screening')
    movie: Mapped['Movie'] = relationship('Movie', back_populates='screening')
    booking: Mapped[list['Booking']] = relationship('Booking', back_populates='screening')