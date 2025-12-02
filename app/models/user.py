# =============================================================================
# User Database Model
# =============================================================================
# SQLAlchemy model for the User table, adapted from the article's DBUser class.
# Modified to work with the existing 'User' table in the PostgreSQL database.
# =============================================================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


# Association table for many-to-many relationship between users and roles
# As described in the article for role-based access control
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id")),
)


class User(Base):
    """
    SQLAlchemy model for the users table.

    Based on the article's DBUser model. Creates a new 'users' table
    to avoid conflicts with any existing 'User' table in the database.
    Stores user authentication data including hashed passwords
    (never plain text as emphasized in article).

    Attributes:
        id: Primary key.
        username: Unique username for authentication.
        email: Unique email address.
        full_name: User's display name.
        hashed_password: Bcrypt hashed password (NEVER store plain text).
        is_active: Whether the user account is active.
        created_at: Timestamp of account creation.
        roles: Many-to-many relationship with Role model.
    """

    __tablename__ = "users"  # New table to avoid conflict with existing 'User' table

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship with roles for authorization
    roles = relationship("Role", secondary=user_roles, back_populates="users")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"
