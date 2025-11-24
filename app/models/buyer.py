from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class Buyer(Base):
    """Model for Buyer-specific data, linked one-to-one to the base User table."""
    
    __tablename__ = "buyer"

    # Primary Key and Foreign Key pointing to User.id
    id = Column(Integer, ForeignKey("User.id"), primary_key=True)
    
    # Specific Columns (Updated based on structure image)
    fullname = Column(String(255), nullable=False) # MUST be NOT NULL

    # Relationship back to the base User
    user = relationship("User", back_populates="buyer")

    def __repr__(self):
        return f"<Buyer(id={self.id}, fullname='{self.fullname}')>"
    