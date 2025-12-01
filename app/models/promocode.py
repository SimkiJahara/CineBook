"""
SQLAlchemy Model for Promocode.
"""

from sqlalchemy import Column, String
from app.core.db import Base 

class Promocode(Base):
    """
    Represents a marketing or discount promocode.
    """
    
    __tablename__ = "promocode"

    # Must match the column referenced in app/models/seat.py: ForeignKey("promocode.code")
    code = Column(String(50), primary_key=True, index=True) 

    def __repr__(self):
        return f"<Promocode(code='{self.code}')>"