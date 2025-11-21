"""
Movie Models - SQLAlchemy ORM
Matches team's NeonDB structure with extensions
"""
from sqlalchemy import Column, String, Integer, Date, Text, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# Association table for Movie <-> Genre (many-to-many)
movie_genre_association = Table(
    'movie_genres',
    Base.metadata,
    Column('movie_eidr', String(50), ForeignKey('movie.eidr'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id'), primary_key=True)
)


class Genre(Base):
    """Genre model for movie categorization"""
    __tablename__ = 'genres'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    movies = relationship('Movie', secondary=movie_genre_association, back_populates='genres')
    
    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}')>"


class Movie(Base):
    """Movie model - matches team's 'movie' table structure"""
    __tablename__ = 'movie'
    
    # Primary key (using EIDR - Entertainment Identifier Registry)
    eidr = Column(String(50), primary_key=True, index=True)
    
    # Basic info (original team columns)
    title = Column(String(255), nullable=False, index=True)
    posterurl = Column(String(255), nullable=True)
    lengthmin = Column(Integer, nullable=True)
    rating = Column(String(10), nullable=True)
    releasedate = Column(Date, nullable=True)
    
    # Extended columns (added for movie module)
    description = Column(Text, nullable=True)
    director = Column(String(200), nullable=True)
    trailerurl = Column(String(255), nullable=True)
    language = Column(String(50), default='English')
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    genres = relationship('Genre', secondary=movie_genre_association, back_populates='movies')
    reviews = relationship('Review', back_populates='movie', cascade='all, delete-orphan')
    cast_members = relationship('MovieCast', back_populates='movie', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Movie(eidr='{self.eidr}', title='{self.title}')>"
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        if not self.reviews:
            return 0.0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)
    
    @property
    def review_count(self):
        """Get total number of reviews"""
        return len(self.reviews) if self.reviews else 0
    
    @property
    def cast(self):
        """Get cast as list of strings"""
        return [c.cast_member for c in self.cast_members] if self.cast_members else []


class MovieCast(Base):
    """Cast members for movies"""
    __tablename__ = 'movie_cast'
    
    id = Column(Integer, primary_key=True, index=True)
    movie_eidr = Column(String(50), ForeignKey('movie.eidr'), nullable=False)
    cast_member = Column(String(200), nullable=False)
    
    # Relationship
    movie = relationship('Movie', back_populates='cast_members')


class Review(Base):
    """Review model for user movie reviews"""
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True, index=True)
    movie_eidr = Column(String(50), ForeignKey('movie.eidr'), nullable=False)
    user_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    rating = Column(Float, nullable=False)
    review_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    movie = relationship('Movie', back_populates='reviews')
    
    def __repr__(self):
        return f"<Review(id={self.id}, movie='{self.movie_eidr}', rating={self.rating})>"