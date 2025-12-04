"""User-related models."""

from typing import TYPE_CHECKING, Optional
from sqlalchemy import Enum, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .review import Reviews
    from .booking import Booking
    from .promocode import Promocode
    from .theater import Theater
    from .screening_draft import Screeningdraft


class User(Base):
    __tablename__ = 'User'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='User_pkey'),
        UniqueConstraint('email', name='User_email_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    passwordhash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(Enum('TheatreOwner', 'Buyer', 'Superadmin', 'TheaterOwner', name='userrole'), nullable=False)

    reviews: Mapped[list['Reviews']] = relationship('Reviews', back_populates='user')


class Buyer(User):
    __tablename__ = 'buyer'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['User.id'], name='buyer_id_fkey'),
        PrimaryKeyConstraint('id', name='buyer_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fullname: Mapped[str] = mapped_column(String(255), nullable=False)

    booking: Mapped[list['Booking']] = relationship('Booking', back_populates='buyer')


class Superadmin(User):
    __tablename__ = 'superadmin'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['User.id'], name='superadmin_id_fkey'),
        PrimaryKeyConstraint('id', name='superadmin_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    promocode: Mapped[list['Promocode']] = relationship('Promocode', back_populates='superadmin')


class Theaterowner(User):
    __tablename__ = 'theaterowner'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['User.id'], name='theaterowner_id_fkey'),
        PrimaryKeyConstraint('id', name='theaterowner_pkey'),
        UniqueConstraint('businessname', name='theaterowner_businessname_key'),
        UniqueConstraint('licensenumber', name='theaterowner_licensenumber_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    businessname: Mapped[str] = mapped_column(String(255), nullable=False)
    ownername: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    licensenumber: Mapped[Optional[str]] = mapped_column(String(100))
    bankdetails: Mapped[Optional[dict]] = mapped_column(JSONB)
    logourl: Mapped[Optional[str]] = mapped_column(String(255))

    screeningdraft: Mapped[list['Screeningdraft']] = relationship('Screeningdraft', back_populates='theaterowner')
    theater: Mapped[list['Theater']] = relationship('Theater', back_populates='theaterowner')