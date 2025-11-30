# /app/models/screen.py (Final Verified Code with Composite FK)

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from app.core.db import Base 

class Screen(Base):
    """Represents a physical screen/hall within a theatre."""

    __tablename__ = "screen" 

    # CRITICAL FIX: Ensure this ID is defined as the Primary Key
    id = Column(Integer, primary_key=True, index=True) 
    
    # Composite Foreign Keys columns for 'theater'
    theatre_company_id = Column(String(50), nullable=False)
    theatre_branch_id = Column(String(50), nullable=False)
    
    name = Column(String, nullable=False) 
    capacity = Column(Integer, nullable=False)

    # Relationships
    theatre = relationship("Theatre", back_populates="screens")
    shows = relationship("Show", back_populates="screen", cascade="all, delete-orphan")
    seats = relationship("Seat", back_populates="screen")

    # Define the composite foreign key constraint
    __table_args__ = (
        ForeignKeyConstraint(
            ['theatre_company_id', 'theatre_branch_id'],
            ['theater.companyid', 'theater.branchid'] # References the composite PK of the Theatre table
        ),
        UniqueConstraint('theatre_company_id', 'theatre_branch_id', 'name', name='_screen_uc'),
    )

    def __repr__(self):
        return f"<Screen(id={self.id}, name='{self.name}')>"