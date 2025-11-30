# /app/models/users.py (Modified)

from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.core.config import UserRole

class User(Base): 
    """Base User Model for all user types."""

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
        foreign_keys="[Booking.user_id]"
    )
    
    # ---------------------------------------------

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"