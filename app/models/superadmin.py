"""
SQLAlchemy Model for the Superadmin user role.

This module defines the Superadmin table, which acts as a simple flag for users
with the highest privileges. It uses a one-to-one relationship with the base User model.
"""

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class Superadmin(Base):
    """
    Model for Superadmin, holds minimal specific data, linked one-to-one to the base :class:`~app.models.users.User` table.

    The primary key serves as a foreign key reference to the :class:`~app.models.users.User` ID,
    implementing the one-to-one extension pattern for role separation.

    :ivar id: Primary key and foreign key to the base User table.
    :vartype id: int
    :ivar user: Relationship back to the parent User object.
    :vartype user: relationship
    """
    
    __tablename__ = "superadmin"

    # Primary Key and Foreign Key pointing to User.id
    id = Column(Integer, ForeignKey("User.id"), primary_key=True)
    
    # Relationship back to the base User
    user = relationship("User", back_populates="superadmin")

    def __repr__(self):
        return f"<Superadmin(id={self.id})>"