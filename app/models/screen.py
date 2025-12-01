"""
SQLAlchemy Model for Screen.

This module defines the Screen table, which represents a physical hall or auditorium
within a theatre. It utilizes a composite foreign key to link back to the Theatre model.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from app.core.db import Base 

class Screen(Base):
    """
    Represents a physical screen/hall within a theatre.

    The Screen is uniquely identified by its internal ID and is associated with a Theatre
    via a composite foreign key referencing the Theatre's company ID and branch ID.

    :ivar id: Unique primary key for the screen/hall.
    :vartype id: int
    :ivar theatre_company_id: Foreign key component: The ID of the theatre company.
    :vartype theatre_company_id: str
    :ivar theatre_branch_id: Foreign key component: The ID of the specific theatre branch.
    :vartype theatre_branch_id: str
    :ivar name: The name of the screen (e.g., "Screen 1", "IMAX Hall").
    :vartype name: str
    :ivar capacity: The total number of seats in the screen.
    :vartype capacity: int
    :ivar theatre: Relationship back to the parent :class:`~app.models.theater.Theatre` object.
    :vartype theatre: relationship
    :ivar shows: Relationship to the :class:`~app.models.show.Show` model, representing
        all shows scheduled for this screen. Deleting a screen deletes associated shows.
    :vartype shows: relationship
    :ivar seats: Relationship to the :class:`~app.models.seat.Seat` model, representing
        all individual seats within this screen.
    :vartype seats: relationship
    """

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