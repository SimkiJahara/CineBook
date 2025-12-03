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

    This model is central to implementing role-based access control (RBAC).
    It stores definitions of roles that can be assigned to users.
    Default roles typically include 'user', 'admin', and 'moderator'.

    :ivar id: Primary key of the role.
    :vartype id: int
    :ivar name: Unique name of the role (e.g., 'user', 'admin', 'moderator').
    :vartype name: str
    :ivar description: Human-readable description of the role.
    :vartype description: str | None
    :ivar users: Many-to-many relationship collection with the :class:`User` model.
    :vartype users: list[:class:`app.models.user.User`]
    """

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)

    # Relationship with users
    users = relationship("User", secondary=user_roles, back_populates="roles")

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"