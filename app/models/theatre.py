from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.core.db import Base # Assuming Base is imported from here

class Theater(Base):
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
    
    # Optional Columns
    contact = Column(String(20), nullable=True) # YES is_nullable
    logourl = Column(String(255), nullable=True) # YES is_nullable
    isverified = Column(Boolean, nullable=True) # YES is_nullable
    
    # Foreign Key linking to the TheaterOwner/User
    # ownerid is int4 (Integer) and NOT NULL
    # Assuming ownerid links to the TheaterOwner table's id (which is User.id)
    ownerid = Column(Integer, ForeignKey("theaterowner.id"), nullable=False)

    # Relationship to the TheaterOwner
    owner = relationship("TheaterOwner", back_populates="theaters")

    def __repr__(self):
        return f"<Theater(companyid={self.companyid}, branchid='{self.branchid}', name='{self.name}')>"

