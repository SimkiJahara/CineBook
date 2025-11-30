# /app/models/theatreowner.py (Corrected)

from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.db import Base


class TheatreOwner(Base):
    """Model for theaterowner-specific data, linked one-to-one to the base User table."""
    
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
    # NOTE: Check if the attribute on the User model is 'theaterowner' or 'theatreowner_profile'
    # Based on your previous code, 'theaterowner' seems correct.
    user = relationship("User", back_populates="theaterowner")
    
    # Relationship to Theatre (one-to-many)
    # FIX: Corrected Indentation of this block
    theatres = relationship(
        "Theatre", 
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TheatreOwner(id={self.id}, businessname='{self.businessname}')>"