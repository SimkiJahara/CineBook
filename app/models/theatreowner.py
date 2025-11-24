from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.db import Base

class TheaterOwner(Base):
    """Model for TheaterOwner-specific data, linked one-to-one to the base User table."""
    
    __tablename__ = "theaterowner"

    # Primary Key and Foreign Key pointing to User.id
    id = Column(Integer, ForeignKey("User.id"), primary_key=True) 
    
    # Specific Columns (Updated based on structure image)
    businessname = Column(String(255), nullable=False)
    ownername = Column(String(20), nullable=False) # MUST be NOT NULL
    phone = Column(String(20), nullable=True) # VARCHAR(20) is nullable
    licensenumber = Column(String(100), nullable=False)
    bankdetails = Column(JSON, nullable=True) # JSON type
    logourl = Column(String(255), nullable=True) # VARCHAR(255) is nullable

    # Relationship back to the base User
    user = relationship("User", back_populates="theaterowner")
    # ⬅️ ADD THE RELATIONSHIP HERE (one-to-many with Theater)
    theaters = relationship("Theater", back_populates="owner")

    def __repr__(self):
        return f"<TheaterOwner(id={self.id}, businessname='{self.businessname}')>"
    