from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class Superadmin(Base):
    """Model for Superadmin, holds minimal specific data, linked one-to-one to the base User table."""
    
    __tablename__ = "superadmin"

    # Primary Key and Foreign Key pointing to User.id
    id = Column(Integer, ForeignKey("User.id"), primary_key=True)
    
    # Relationship back to the base User
    user = relationship("User", back_populates="superadmin")

    def __repr__(self):
        return f"<Superadmin(id={self.id})>"