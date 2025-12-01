"""
SQLAlchemy Base User Model.

This module defines the central User model, from which all specific user roles 
(Buyer, TheatreOwner, Superadmin) extend via one-to-one relationships. It also 
maintains relationships to real-time seat reservations and final bookings.
"""

from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.core.config import UserRole

class User(Base): 
    """
    Base User Model for all user types.

    This model serves as the authentication and core identity record. It is linked
    to specialized role tables using one-to-one relationships.

    :ivar id: Unique primary key of the user.
    :vartype id: int
    :ivar email: Unique email address of the user (used for login).
    :vartype email: str
    :ivar name: The user's display name or full name (optional in base).
    :vartype name: str
    :ivar passwordhash: The bcrypt hashed password (required).
    :vartype passwordhash: str
    :ivar role: The assigned role of the user (e.g., Buyer, TheatreOwner, Superadmin).
    :vartype role: app.core.config.UserRole
    :ivar theaterowner: Relationship to the :class:`~app.models.theatreowner.TheatreOwner` profile.
    :vartype theaterowner: relationship
    :ivar superadmin: Relationship to the :class:`~app.models.superadmin.Superadmin` profile.
    :vartype superadmin: relationship
    :ivar buyer: Relationship to the :class:`~app.models.buyer.Buyer` profile.
    :vartype buyer: relationship
    :ivar reserved_seats: Relationship to the :class:`~app.models.seat.ShowSeat` model, linking to seats 
        currently held (reserved, status=PENDING) by this user.
    :vartype reserved_seats: relationship
    :ivar bookings: Relationship to the :class:`~app.models.seat.Booking` model, linking to final 
        confirmed bookings made by this user (as a Buyer).
    :vartype bookings: relationship
    """

    __tablename__ = "User"

    id= Column(Integer, primary_key=True, index=True)
    
    email= Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    passwordhash= Column(String, nullable= False)
    role = Column(Enum(UserRole), default=UserRole.buyer, nullable=False)


    # Relationships to the specialized tables (One-to-One)
    theaterowner = relationship("TheatreOwner", back_populates="user", uselist=False)
    superadmin = relationship("Superadmin", back_populates="user", uselist=False)
    buyer = relationship("Buyer", back_populates="user", uselist=False)

    # --- NEW RELATIONSHIPS FOR BOOKING FEATURE ---
    
    # Links to seats currently held by this user (ShowSeat.reserved_by_user_id)
    # The 'foreign_keys' argument ensures SQLAlchemy knows which FK column to use.
    reserved_seats = relationship(
        "ShowSeat", 
        back_populates="reserved_by",
        foreign_keys="[ShowSeat.reserved_by_user_id]" 
    )

    # Links to final confirmed bookings made by this user (Booking.user_id)
    bookings = relationship(
        "Booking", 
        back_populates="user", 
        foreign_keys="[Booking.buyerid]"
    )
    
    # ---------------------------------------------

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"