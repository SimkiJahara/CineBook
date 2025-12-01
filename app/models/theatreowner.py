"""
SQLAlchemy Model for TheatreOwner.

This module defines the TheatreOwner table, which stores specialized information 
for users with the 'TheatreOwner' role. It uses a one-to-one relationship with 
the base User model and a one-to-many relationship with the Theatre model.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.db import Base


class TheatreOwner(Base):
    """
    Model for theaterowner-specific data, linked one-to-one to the base :class:`~app.models.users.User` table.

    The primary key serves as a foreign key reference to the :class:`~app.models.users.User` ID.

    :ivar id: Primary key and foreign key to the base User table.
    :vartype id: int
    :ivar businessname: The registered name of the business or company owned by the user.
    :vartype businessname: str
    :ivar ownername: The full name of the primary contact/owner.
    :vartype ownername: str
    :ivar phone: Contact phone number.
    :vartype phone: str
    :ivar licensenumber: Mandatory official business license number.
    :vartype licensenumber: str
    :ivar bankdetails: JSON field storing banking or payment processing details (e.g., {"account_id": "...", "routing": "..."}).
    :vartype bankdetails: JSON
    :ivar logourl: URL to the business logo.
    :vartype logourl: str
    :ivar user: Relationship back to the parent :class:`~app.models.users.User` object.
    :vartype user: relationship
    :ivar theatres: Relationship to the :class:`~app.models.theatre.Theatre` model (one-to-many). Represents all
        theatres managed by this owner. Deleting the owner deletes their theatres.
    :vartype theatres: relationship
    """
    
    __tablename__ = "theatreowner" # NOTE: Using lowercase table name 'theatreowner'

    # Foreign Key from User table (assuming User table name is "User")
    id = Column(Integer, ForeignKey("User.id"), primary_key=True) 
    
    # Specific Columns
    businessname = Column(String(255), nullable=False)
    ownername = Column(String(20), nullable=False) 
    phone = Column(String(20), nullable=True) 
    licensenumber = Column(String(100), nullable=False)
    bankdetails = Column(JSON, nullable=True) 
    logourl = Column(String(255), nullable=True) 

    # Relationship back to the base User
    user = relationship("User", back_populates="theaterowner")
    
    # Relationship to Theatre (one-to-many)
    theatres = relationship(
        "Theatre", 
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TheatreOwner(id={self.id}, businessname='{self.businessname}')>"