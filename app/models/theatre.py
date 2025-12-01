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

    The model uses a **composite primary key** consisting of ``companyid`` and 
    ``branchid``. It links to the :class:`~app.models.theatreowner.TheatreOwner` 
    and has a complex relationship with :class:`~app.models.screen.Screen`.

    :ivar companyid: Component of the composite primary key: Unique identifier for the theatre company.
    :vartype companyid: str
    :ivar branchid: Component of the composite primary key: Unique identifier for the specific branch location.
    :vartype branchid: str
    :ivar name: The human-readable name of the theatre branch (e.g., "PVR Phoenix").
    :vartype name: str
    :ivar address: The physical address of the theatre.
    :vartype address: str
    :ivar contact: Primary contact number for the theatre.
    :vartype contact: str
    :ivar logourl: URL to the theatre's logo image.
    :vartype logourl: str
    :ivar isverified: Boolean flag indicating if the theatre has been verified by an admin.
    :vartype isverified: bool
    :ivar ownerid: Foreign key to the ID of the :class:`~app.models.theatreowner.TheatreOwner` who manages this theatre.
    :vartype ownerid: int
    :ivar owner: Relationship back to the managing :class:`~app.models.theatreowner.TheatreOwner` object.
    :vartype owner: relationship
    :ivar screens: Relationship to the :class:`~app.models.screen.Screen` model (one-to-many). The join is explicitly 
        defined using the composite key columns. Deleting a theatre deletes all its screens.
    :vartype screens: relationship
    """
    
    __tablename__ = "theater" # NOTE: Table name is "theater"

    # Composite Primary Key on companyid and branchid (from user's original code)
    companyid = Column(String(50), nullable=False)
    branchid = Column(String(50), nullable=False)
    
    # Define the composite primary key
    __table_args__ = (
        PrimaryKeyConstraint(companyid, branchid, name='theater_pkey'),
    )

    # Core Columns
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    contact = Column(String(20), nullable=True)
    logourl = Column(String(255), nullable=True)
    isverified = Column(Boolean, nullable=True)
    
    # Foreign Key linking to the TheaterOwner
    ownerid = Column(Integer, ForeignKey("theaterowner.id"), nullable=False)

    # Relationship to the TheaterOwner
    owner = relationship("TheatreOwner", back_populates="theatres")

    # Relationship to Screen (one-to-many) - CRITICAL COMPOSITE KEY UPDATE
    # The primaryjoin explicitly links Theatre's PK columns to the FK columns in Screen.
    screens = relationship(
        "Screen", 
        back_populates="theatre",
        primaryjoin="and_(Theatre.companyid==Screen.theatre_company_id, Theatre.branchid==Screen.theatre_branch_id)",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Theater(companyid={self.companyid}, branchid='{self.branchid}', name='{self.name}')>"