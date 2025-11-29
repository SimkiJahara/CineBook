from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.core.db import Base 


class Theatre(Base):
    """Model for a specific Theater location/branch."""
    
    __tablename__ = "theater"

    # Composite Primary Key on companyid and branchid
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
    # This correctly uses "TheatreOwner" and the correct back_populates name "theatres"
    owner = relationship("TheatreOwner", back_populates="theatres")

    def __repr__(self):
        return f"<Theater(companyid={self.companyid}, branchid='{self.branchid}', name='{self.name}')>"