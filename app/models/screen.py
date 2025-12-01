"""
SQLAlchemy Model for Screen.
...
"""

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from app.core.db import Base 

class Screen(Base):
    """
    Represents a physical screen/hall within a theatre.
    ...
    """

    __tablename__ = "screen" 
    
    # FIX: Add extend_existing=True for robustness against circular imports.
    __table_args__ = (
        ForeignKeyConstraint(
            ['theatre_company_id', 'theatre_branch_id'],
            ['theatre.companyid', 'theatre.branchid'] # 💡 FIX: Changed from "theater.companyid" to "theatre.companyid"
        ),
        UniqueConstraint('theatre_company_id', 'theatre_branch_id', 'name', name='_screen_uc'),
        {'extend_existing': True} 
    )


    id = Column(Integer, primary_key=True, index=True) 
    
    # Composite Foreign Keys columns for 'theatre'
    theatre_company_id = Column(String(50), nullable=False)
    theatre_branch_id = Column(String(50), nullable=False)
    
    name = Column(String, nullable=False) 
    capacity = Column(Integer, nullable=False)

    # Relationships
    theatre = relationship("Theatre", back_populates="screens")
    
    # Corrected target to "Screening" and property name to 'screenings'
    screenings = relationship("Screening", back_populates="screen", cascade="all, delete-orphan")
    
    seats = relationship("Seat", back_populates="screen", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Screen(id={self.id}, name='{self.name}')>"