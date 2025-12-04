"""Movie-related models."""

import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, Date, DateTime, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .review import Reviews
    from .screening import Screening


class Genres(Base):
    __tablename__ = 'genres'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='genres_pkey'),
        UniqueConstraint('name', name='genres_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    movie: Mapped[list['Movie']] = relationship('Movie', secondary='movie_genres', back_populates='genre')


class Movie(Base):
    __tablename__ = 'movie'
    __table_args__ = (
        PrimaryKeyConstraint('eidr', name='movie_pkey'),
        Index('idx_movie_releasedate', 'releasedate'),
        Index('idx_movie_title', 'title')
    )

    eidr: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    posterurl: Mapped[Optional[str]] = mapped_column(String(255))
    lengthmin: Mapped[Optional[int]] = mapped_column(Integer)
    rating: Mapped[Optional[str]] = mapped_column(String(10))
    releasedate: Mapped[Optional[datetime.date]] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(Text)
    director: Mapped[Optional[str]] = mapped_column(String(200))
    trailerurl: Mapped[Optional[str]] = mapped_column(String(255))
    language: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'English'::character varying"))
    is_active: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('1'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    genre: Mapped[list['Genres']] = relationship('Genres', secondary='movie_genres', back_populates='movie')
    movie_cast: Mapped[list['MovieCast']] = relationship('MovieCast', back_populates='movie')
    reviews: Mapped[list['Reviews']] = relationship('Reviews', back_populates='movie')
    screening: Mapped[list['Screening']] = relationship('Screening', back_populates='movie')


class MovieCast(Base):
    __tablename__ = 'movie_cast'
    __table_args__ = (
        ForeignKeyConstraint(['movie_eidr'], ['movie.eidr'], ondelete='CASCADE', name='movie_cast_movie_eidr_fkey'),
        PrimaryKeyConstraint('id', name='movie_cast_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cast_member: Mapped[str] = mapped_column(String(200), nullable=False)
    movie_eidr: Mapped[Optional[str]] = mapped_column(String(50))

    movie: Mapped[Optional['Movie']] = relationship('Movie', back_populates='movie_cast')


t_movie_genres = Table(
    'movie_genres', Base.metadata,
    Column('movie_eidr', String(50), primary_key=True),
    Column('genre_id', Integer, primary_key=True),
    ForeignKeyConstraint(['genre_id'], ['genres.id'], ondelete='CASCADE', name='movie_genres_genre_id_fkey'),
    ForeignKeyConstraint(['movie_eidr'], ['movie.eidr'], ondelete='CASCADE', name='movie_genres_movie_eidr_fkey'),
    PrimaryKeyConstraint('movie_eidr', 'genre_id', name='movie_genres_pkey'),
    Index('idx_movie_genres_movie', 'movie_eidr')
)