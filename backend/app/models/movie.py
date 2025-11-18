from sqlalchemy import Column, String, Integer, Date, ARRAY, Table, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

# Many-to-Many association table for Movie and Genre
movie_genre_association = Table(
    'movie_genres',
    Base.metadata,
    Column('movie_eidr', String, ForeignKey('movies.eidr', ondelete='CASCADE')),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete='CASCADE'))
)

class Movie(Base):
    __tablename__ = "movies"
    
    eidr = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    poster_url = Column(String)
    language = Column(String)
    duration_min = Column(Integer)
    rating = Column(String)
    cast = Column(ARRAY(String))
    release_date = Column(Date)
    
    # Relationships
    genres = relationship(
        "Genre",
        secondary=movie_genre_association,
        back_populates="movies"
    )
    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")

class Genre(Base):
    __tablename__ = "genres"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    
    # Relationships
    movies = relationship(
        "Movie",
        secondary=movie_genre_association,
        back_populates="genres"
    )
