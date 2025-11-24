from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.core.config import UserRole

class User(Base): 
    """Base User Model for all user types."""

    __tablename__ = "User"

    id= Column(Integer, primary_key=True, index=True)
    
    email= Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    passwordhash= Column(String, nullable= False)
    role = Column(Enum(UserRole), default=UserRole.buyer, nullable=False)


    # Relationships to the specialized tables (One-to-One)
    theaterowner = relationship("TheaterOwner", back_populates="users", uselist=False)
    superadmin = relationship("Superadmin", back_populates="users", uselist=False)
    buyer = relationship("Buyer", back_populates="users", uselist=False)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

