# /app/models/seat.py (FIXED CODE)

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Enum, DateTime, ForeignKey, 
    UniqueConstraint, ForeignKeyConstraint, Numeric # Added Numeric for totalamount
)
from sqlalchemy.orm import relationship

from app.core.db import Base 
# Note: You MUST ensure 'Screening' model is imported here if it's used in relationships
# from app.models.show import Screening 
# and 'Buyer' model from app.models.buyer import Buyer if relationships are used directly

# --- Enums ---

class SeatStatus(enum.Enum):
    """
    Status of a seat for a specific show.
    """
    AVAILABLE = "Available"
    PENDING = "Pending"
    BOOKED = "Booked"

class BookingStatus(enum.Enum):
    """
    Status of a final booking transaction.
    (Matches the ENUM type defined in CineBookSchema.sql)
    """
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

# --- Models ---

class Seat(Base):
    """
    Represents a physical seat.
    FIX: Matches the composite primary key and columns of the public.seat table.
    """
    __tablename__ = "seat"
    
    # FIX: Composite Primary Key columns from schema
    seatid = Column(String(50), primary_key=True) 
    layouthallid = Column(String(50), primary_key=True) 
    layoutcompanyid = Column(String(50), primary_key=True) 
    layoutbranchid = Column(String(50), primary_key=True) 
    
    # Other columns (corrected names from schema)
    rownumber = Column(String(10), nullable=False)  
    number = Column(Integer, nullable=False)        
    type = Column(String(50), nullable=True)
    status = Column(String(50), default='AVAILABLE')

    # Relationships
    show_seats = relationship("ShowSeat", back_populates="seat")

    __table_args__ = (
        # Foreign Key to seatlayout table
        ForeignKeyConstraint(
            ['layouthallid', 'layoutcompanyid', 'layoutbranchid'],
            ['seatlayout.layouthallid', 'seatlayout.layoutcompanyid', 'seatlayout.layoutbranchid'],
            name='fk_seat_seatlayout'
        ),
    )


class ShowSeat(Base):
    """
    Core table for real-time booking.
    FIX: Uses composite foreign key to Seat and references the renamed 'screening' table.
    """
    __tablename__ = "show_seat"

    id = Column(Integer, primary_key=True, index=True)
    
    # FIX: Foreign Key references the renamed table 'screening'
    screening_id = Column(Integer, ForeignKey("screening.id"), index=True, nullable=False)
    
    # FIX: Columns for composite Foreign Key to Seat table
    # Renamed to clearly differentiate from the simple ShowSeat.id
    seat_seatid = Column(String(50), index=True, nullable=False) 
    seat_layouthallid = Column(String(50), nullable=False) 
    seat_layoutcompanyid = Column(String(50), nullable=False) 
    seat_layoutbranchid = Column(String(50), nullable=False) 
    
    reserved_by_user_id = Column(Integer, ForeignKey("User.id"), nullable=True, index=True) 
    
    status = Column(Enum(SeatStatus), default=SeatStatus.AVAILABLE, nullable=False)
    hold_expiry_time = Column(DateTime, nullable=True) 
    
    # Relationships
    # FIX: Renamed 'show' to 'screening' and ensures correct FK columns are used
    screening = relationship("Screening", back_populates="show_seats", foreign_keys=[screening_id])
    
    seat = relationship("Seat", 
                        primaryjoin="and_(ShowSeat.seat_seatid == Seat.seatid, "
                                    "ShowSeat.seat_layouthallid == Seat.layouthallid, "
                                    "ShowSeat.seat_layoutcompanyid == Seat.layoutcompanyid, "
                                    "ShowSeat.seat_layoutbranchid == Seat.layoutbranchid)",
                        foreign_keys=[seat_seatid, seat_layouthallid, seat_layoutcompanyid, seat_layoutbranchid],
                        back_populates="show_seats")
    reserved_by = relationship("User", back_populates="reserved_seats", foreign_keys="[ShowSeat.reserved_by_user_id]")


    __table_args__ = (
        # FIX: Composite Foreign Key Constraint to Seat table
        ForeignKeyConstraint(
            ['seat_seatid', 'seat_layouthallid', 'seat_layoutcompanyid', 'seat_layoutbranchid'],
            ['seat.seatid', 'seat.layouthallid', 'seat.layoutcompanyid', 'seat.layoutbranchid'],
            name='fk_showseat_seat'
        ),
        # FIX: Unique constraint now reflects the composite nature of the seat key
        UniqueConstraint('screening_id', 'seat_seatid', 'seat_layouthallid', 'seat_layoutcompanyid', 'seat_layoutbranchid', name='_show_seat_uc'),
    )


class Booking(Base):
    """
    Represents a final confirmed booking transaction.
    FIX: Column names match the public.booking table in CineBookSchema.sql.
    """
    __tablename__ = "booking"

    # FIX: Primary key name is 'bookingid'
    bookingid = Column(Integer, primary_key=True, index=True) 
    
    # FIX: User ID is 'buyerid' referencing 'buyer'
    buyerid = Column(Integer, ForeignKey("buyer.id"), nullable=False)
    
    # FIX: Show ID is 'screeningid' referencing 'screening'
    screeningid = Column(Integer, ForeignKey("screening.id"), nullable=False)
    
    # FIX: Column names and types match schema
    bookedat = Column(DateTime, default=datetime.utcnow, nullable=False) 
    totalamount = Column(Numeric(10,2), nullable=False) 
    paymentmethod = Column(String(50), nullable=False) 
    status = Column(Enum(BookingStatus), default=BookingStatus.CONFIRMED, nullable=False)
    
    # Additional columns from schema
    qrcodeurl = Column(String(255), nullable=True)
    promocode = Column(String(50), ForeignKey("promocode.code"), nullable=True)


    # relationships
    user = relationship("Buyer", back_populates="bookings", foreign_keys="[Booking.buyerid]")
    # FIX: Renamed 'show' to 'screening'
    screening = relationship("Screening", back_populates="bookings", foreign_keys="[Booking.screeningid]") 
    booked_seats = relationship("BookedSeat", back_populates="booking")


class BookedSeat(Base):
    """
    Mapping table between a Booking and the individual seats confirmed.
    FIX: Table name and foreign key reference 'booking.bookingid'.
    """
    __tablename__ = "bookingseat" # FIX: Correct schema table name
    
    id = Column(Integer, primary_key=True, index=True) # Retaining simple PK for SQLAlchemy model ease
    
    # FIX: Foreign Key references the 'bookingid' primary key on the booking table
    booking_id = Column(Integer, ForeignKey("booking.bookingid"), nullable=False) 
    show_seat_id = Column(Integer, ForeignKey("show_seat.id"), nullable=False, unique=True)
    
    booking = relationship("Booking", back_populates="booked_seats", foreign_keys=[booking_id])
    show_seat = relationship("ShowSeat", foreign_keys=[show_seat_id])