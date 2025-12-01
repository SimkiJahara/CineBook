"""
SQLAlchemy Model for the Buyer user role.

This module defines the Buyer table, which holds specialized information for users
with the 'Buyer' role. It uses a one-to-one relationship with the base User model.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class Buyer(Base):
    """
    Model for Buyer-specific data, linked one-to-one to the base :class:`~app.models.users.User` table.

    The primary key serves as a foreign key reference to the :class:`~app.models.users.User` ID,
    implementing the one-to-one extension pattern.

    :ivar id: Primary key and foreign key to the base User table.
    :vartype id: int
    :ivar fullname: The full name of the buyer user (required).
    :vartype fullname: str
    :ivar user: Relationship back to the parent User object.
    :vartype user: relationship
    :ivar bookings: Relationship to the :class:`~app.models.seat.Booking` model, listing all confirmed bookings made by this buyer.
    :vartype bookings: relationship
    """
    
    __tablename__ = "buyer"

    # Primary Key and Foreign Key pointing to User.id
    id = Column(Integer, ForeignKey("User.id"), primary_key=True)
    
    # Specific Columns (Updated based on structure image)
    fullname = Column(String(255), nullable=False) # MUST be NOT NULL

    # Relationship back to the base User
    user = relationship("User", back_populates="buyer")
    
    # FIX: Added the 'overlaps' parameter to suppress the warning about ambiguous relationships
    # caused by the inheritance structure (Buyer is linked to User, which is also linked to Booking).
    bookings = relationship(
        "Booking", 
        back_populates="user", 
        cascade="all, delete-orphan",
        overlaps="user,bookings"
    )

    def __repr__(self):
        return f"<Buyer(id={self.id}, fullname='{self.fullname}')>"