"""
SQLAlchemy Model for Theatre.

This module defines the Theatre model (named 'theater' in the database), which 
represents a specific theatre location or branch. It is defined with a composite 
primary key and links back to the TheatreOwner and Screen models.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.core.db import Base 


class Theatre(Base):
    """
    Model for a specific Theater location/branch.
    ...
    """
    
    __tablename__ = "theatre" # 💡 FIX: Changed from "theater" to "theatre"

    # Composite Primary Key on companyid and branchid (from user's original code)
    companyid = Column(String(50), nullable=False)
    branchid = Column(String(50), nullable=False)
    
    # Define the composite primary key
    __table_args__ = (
        PrimaryKeyConstraint(companyid, branchid, name='theatre_pkey'), # 💡 Also update pkey name
    )

    # Core Columns
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    contact = Column(String(20), nullable=True)
    logourl = Column(String(255), nullable=True)
    isverified = Column(Boolean, nullable=True)
    
    # Foreign Key linking to the TheaterOwner (this was already consistently spelled)
    ownerid = Column(Integer, ForeignKey("theatreowner.id"), nullable=False)

    # Relationship to the TheaterOwner
    owner = relationship(
        "TheatreOwner", 
        back_populates="theatres",
        foreign_keys=[ownerid] 
    )

    # Relationship to Screen (one-to-many) - CRITICAL COMPOSITE KEY UPDATE
    screens = relationship(
        "Screen", 
        back_populates="theatre",
        primaryjoin="and_(Theatre.companyid==Screen.theatre_company_id, Theatre.branchid==Screen.theatre_branch_id)",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Theatre(companyid={self.companyid}, branchid='{self.branchid}', name='{self.name}')>"