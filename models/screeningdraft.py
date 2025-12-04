"""Screening draft model."""

import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import Theaterowner


class Screeningdraft(Base):
    __tablename__ = 'screeningdraft'
    __table_args__ = (
        ForeignKeyConstraint(['ownerid'], ['theaterowner.id'], name='screeningdraft_ownerid_fkey'),
        PrimaryKeyConstraint('id', name='screeningdraft_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ownerid: Mapped[int] = mapped_column(Integer, nullable=False)
    createdat: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    draftdata: Mapped[Optional[dict]] = mapped_column(JSONB)

    theaterowner: Mapped['Theaterowner'] = relationship('Theaterowner', back_populates='screeningdraft')