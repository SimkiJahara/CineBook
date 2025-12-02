# =============================================================================
# Role Database Model
# =============================================================================
# SQLAlchemy model for the Role table, implementing role-based access control
# as described in the article's database section.
# =============================================================================

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.user import user_roles


class Role(Base):
    """
    SQLAlchemy model for the Role table.

    As described in the article: Implements role-based access control.
    Default roles include 'user', 'admin', and 'moderator'.

    Attributes:
        id: Primary key.
        name: Unique role name (e.g., 'user', 'admin', 'moderator').
        description: Human-readable description of the role.
        users: Many-to-many relationship with User model.
    """

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)

    # Relationship with users
    users = relationship("User", secondary=user_roles, back_populates="roles")

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"
