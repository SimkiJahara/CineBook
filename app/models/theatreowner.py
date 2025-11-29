from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.db import Base


class TheatreOwner(Base):
    """Model for theaterowner-specific data, linked one-to-one to the base User table."""
    
    __tablename__ = "theaterowner"

    id = Column(Integer, ForeignKey("User.id"), primary_key=True) 
    
    # Specific Columns
    businessname = Column(String(255), nullable=False)
    ownername = Column(String(20), nullable=False) 
    phone = Column(String(20), nullable=True) 
    licensenumber = Column(String(100), nullable=False)
    bankdetails = Column(JSON, nullable=True) 
    logourl = Column(String(255), nullable=True) 

    # Relationship back to the base User
    # CRITICAL: Assuming 'theaterowner' is the attribute name on the User model.
    user = relationship("User", back_populates="theaterowner")
    
    # Relationship to Theatre (one-to-many)
    # FIX: Change target string from "theatre" (lowercase) to "Theatre" (PascalCase) 
    # to match the actual class name.
    theatres = relationship("Theatre", back_populates="owner")

    def __repr__(self):
        return f"<TheatreOwner(id={self.id}, businessname='{self.businessname}')>"