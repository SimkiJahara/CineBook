from sqlalchemy import Column, String, Integer, DateTime, Date, Text, ForeignKey, Table, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


# Association Tables
movie_genre_association = Table(
    'movie_genres',
    Base.metadata,
    Column('movie_eidr', String(50), ForeignKey('movies.eidr'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id'), primary_key=True)
)

movie_cast_association = Table(
    'movie_cast',
    Base.metadata,
    Column('movie_eidr', String(50), ForeignKey('movies.eidr'), primary_key=True),
    Column('cast_member', String(200), primary_key=True)
)


class Genre(Base):
    """Genre model for movie categorization"""
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    movies = relationship('Movie', secondary=movie_genre_association, back_populates='genres')

    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}')>"


class Movie(Base):
    """Movie model representing film information"""
    __tablename__ = 'movies'

    eidr = Column(String(50), primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    poster_url = Column(String(500), nullable=True)
    language = Column(String(50), nullable=False)
    duration_min = Column(Integer, nullable=False)
    rating = Column(String(10), nullable=True)
    release_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    director = Column(String(200), nullable=True)
    trailer_url = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Integer, default=1)

    # Relationships
    genres = relationship('Genre', secondary=movie_genre_association, back_populates='movies')
    reviews = relationship('Review', back_populates='movie', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Movie(eidr='{self.eidr}', title='{self.title}')>"

    @property
    def average_rating(self):
        if not self.reviews:
            return 0.0
        return round(sum(review.rating for review in self.reviews) / len(self.reviews), 1)

    @property
    def review_count(self):
        return len(self.reviews)


class Review(Base):
    """Review model for user movie reviews"""
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movie_eidr = Column(String(50), ForeignKey('movies.eidr'), nullable=False)
    # ← Temporarily removed ForeignKey to non-existent 'users' table
    user_id = Column(String(50), nullable=False)  # dummy user until User model exists
    rating = Column(Float, nullable=False)
    review_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    movie = relationship('Movie', back_populates='reviews')

    def __repr__(self):
        return f"<Review(id={self.id}, movie='{self.movie_eidr}', rating={self.rating})>"