"""Reviews model."""

import datetime
import decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import CheckConstraint, DateTime, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .movie import Movie
    from .user import User


class Reviews(Base):
    __tablename__ = 'reviews'
    __table_args__ = (
        CheckConstraint('rating >= 1.0 AND rating <= 5.0', name='reviews_rating_check'),
        ForeignKeyConstraint(['movie_eidr'], ['movie.eidr'], ondelete='CASCADE', name='reviews_movie_eidr_fkey'),
        ForeignKeyConstraint(['user_id'], ['User.id'], ondelete='CASCADE', name='reviews_user_id_fkey'),
        PrimaryKeyConstraint('id', name='reviews_pkey'),
        UniqueConstraint('movie_eidr', 'user_id', name='reviews_movie_eidr_user_id_key'),
        Index('idx_reviews_movie', 'movie_eidr')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    movie_eidr: Mapped[Optional[str]] = mapped_column(String(50))
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    rating: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(2, 1))
    review_text: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    movie: Mapped[Optional['Movie']] = relationship('Movie', back_populates='reviews')
    user: Mapped[Optional['User']] = relationship('User', back_populates='reviews')