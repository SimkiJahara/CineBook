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
"""
SQLAlchemy :class:`~sqlalchemy.Table` defining the many-to-many relationship
between the :class:`User` model and the :class:`Role` model.
"""


class User(Base):
    """
    SQLAlchemy model for the users table.

    Based on the article's DBUser model. Stores user authentication and profile data.
    Passwords are stored as bcrypt hashes (NEVER plain text).

    :ivar id: Primary key of the user.
    :vartype id: int
    :ivar username: Unique username used for authentication.
    :vartype username: str
    :ivar email: Unique email address.
    :vartype email: str
    :ivar full_name: User's display name.
    :vartype full_name: str | None
    :ivar hashed_password: Bcrypt hashed password.
    :vartype hashed_password: str
    :ivar is_active: Status indicating whether the user account is active. Defaults to True.
    :vartype is_active: bool
    :ivar created_at: Timestamp of account creation. Defaults to the current time.
    :vartype created_at: :class:`datetime.datetime`
    :ivar roles: Many-to-many relationship collection with the :class:`Role` model via :data:`user_roles`.
    :vartype roles: list[:class:`app.models.role.Role`]
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