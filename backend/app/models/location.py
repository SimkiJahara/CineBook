from sqlalchemy import column, Integer, String, ForeignKey
from app.utils.database import Base

class City(Base):
    """creates a City model/table in database"""
    
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    

class Address(Base):
    """
    creates a Address table in database 
    """
    
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    street = Column(String(100), nullable=False)
    area = Column(String(100),nullable=False)
    postal_code = Column(String(20),nullable=False)


class Theater(Base):
    """
    it creates a Theatre table in database,
    and this table is connected to city and address table
    as every theatre should have city and address
    """
    
    __tablename__ = "theaters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, unique=True)
    description = Column(String(300), nullable=True)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    
    # Foreign Keys 
    
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    

class Hall(Base):
    """
    details about  hall inside a theater where movies are screened.
    """

    __tablename__ = "halls"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    total_seats = Column(Integer, nullable=False)

    theater_id = Column(Integer, ForeignKey("theaters.id"), nullable=False)


class Screening(Base):
    """
    Screening of a movie , which include hall,date,time
    """
    
    __tablename__ = "screenings"

    id = Column(Integer, primary_key=True, index=True)

    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    hall_id = Column(Integer, ForeignKey("halls.id"), nullable=False)

    show_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)

    base_price = Column(Numeric(10, 2), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
