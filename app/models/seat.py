"""
SQLAlchemy Models for Seats and Bookings.

This module defines the models related to physical seats, the real-time status
of seats for specific shows (ShowSeat), the final confirmed booking transaction (Booking),
and the mapping of booked seats (BookedSeat).

It includes complex composite primary and foreign key definitions.
"""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Enum, DateTime, ForeignKey, 
    UniqueConstraint, ForeignKeyConstraint, Numeric
)
from sqlalchemy.orm import relationship

from app.core.db import Base 
# Note: Assuming Screening model is available globally or imported in other modules
# where relationships are resolved.

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
    Represents a physical seat in a screen layout.

    This model uses a **composite primary key** to uniquely identify a seat 
    within a specific theatre's hall/layout.

    :ivar seatid: Component of the composite primary key: The seat's identifier (e.g., 'A1').
    :vartype seatid: str
    :ivar layouthallid: Component of the composite primary key: The ID of the layout hall (Screen).
    :vartype layouthallid: str
    :ivar layoutcompanyid: Component of the composite primary key: The ID of the theatre company.
    :vartype layoutcompanyid: str
    :ivar layoutbranchid: Component of the composite primary key: The ID of the theatre branch.
    :vartype layoutbranchid: str
    :ivar rownumber: The row identifier (e.g., 'A', 'B').
    :vartype rownumber: str
    :ivar number: The column/number identifier of the seat.
    :vartype number: int
    :ivar type: The type of seat (e.g., 'Standard', 'VIP').
    :vartype type: str
    :ivar status: The general status of the seat type.
    :vartype status: str
    :ivar show_seats: Relationship to the :class:`ShowSeat` model, linking this physical seat to its status in all screenings.
    :vartype show_seats: relationship
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
    Core table for real-time booking, representing the dynamic status of a seat for a specific screening.

    This model uses a **composite unique constraint** across the screening ID and the seat's four composite foreign keys.

    :ivar id: Primary key for the show seat record.
    :vartype id: int
    :ivar screening_id: Foreign key to the :class:`~app.models.show.Screening` table.
    :vartype screening_id: int
    :ivar seat_seatid: Component of the composite foreign key to :class:`Seat`.
    :vartype seat_seatid: str
    :ivar seat_layouthallid: Component of the composite foreign key to :class:`Seat`.
    :vartype seat_layouthallid: str
    :ivar seat_layoutcompanyid: Component of the composite foreign key to :class:`Seat`.
    :vartype seat_layoutcompanyid: str
    :ivar seat_layoutbranchid: Component of the composite foreign key to :class:`Seat`.
    :vartype seat_layoutbranchid: str
    :ivar reserved_by_user_id: Foreign key to the :class:`~app.models.users.User` who currently holds the seat (optional).
    :vartype reserved_by_user_id: int
    :ivar status: Real-time status of the seat (Available, Pending, Booked).
    :vartype status: SeatStatus
    :ivar hold_expiry_time: Timestamp when a PENDING hold expires, releasing the seat.
    :vartype hold_expiry_time: datetime.datetime
    :ivar screening: Relationship back to the parent Screening object.
    :vartype screening: relationship
    :ivar seat: Relationship back to the physical :class:`Seat` object.
    :vartype seat: relationship
    :ivar reserved_by: Relationship back to the :class:`~app.models.users.User` who holds the reservation.
    :vartype reserved_by: relationship
    """
    __tablename__ = "show_seat"

    id = Column(Integer, primary_key=True, index=True)
    
    # FIX: Foreign Key references the renamed table 'screening'
    screening_id = Column(Integer, ForeignKey("screening.id"), index=True, nullable=False)
    
    # FIX: Columns for composite Foreign Key to Seat table
    seat_seatid = Column(String(50), index=True, nullable=False) 
    seat_layouthallid = Column(String(50), nullable=False) 
    seat_layoutcompanyid = Column(String(50), nullable=False) 
    seat_layoutbranchid = Column(String(50), nullable=False) 
    
    reserved_by_user_id = Column(Integer, ForeignKey("User.id"), nullable=True, index=True) 
    
    status = Column(Enum(SeatStatus), default=SeatStatus.AVAILABLE, nullable=False)
    hold_expiry_time = Column(DateTime, nullable=True) 
    
    # Relationships
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
    Represents a final confirmed booking transaction (e.g., ticket purchase).

    :ivar bookingid: Primary key of the booking transaction.
    :vartype bookingid: int
    :ivar buyerid: Foreign key to the :class:`~app.models.buyer.Buyer` who made the booking.
    :vartype buyerid: int
    :ivar screeningid: Foreign key to the :class:`~app.models.show.Screening` that was booked.
    :vartype screeningid: int
    :ivar bookedat: Timestamp of when the booking was confirmed.
    :vartype bookedat: datetime.datetime
    :ivar totalamount: The total price of the transaction.
    :vartype totalamount: Decimal
    :ivar paymentmethod: The method used for payment.
    :vartype paymentmethod: str
    :ivar status: The final status of the booking (Confirmed, Cancelled, etc.).
    :vartype status: BookingStatus
    :ivar qrcodeurl: URL for the QR code used for entry.
    :vartype qrcodeurl: str
    :ivar promocode: Optional foreign key to a valid promo code used.
    :vartype promocode: str
    :ivar user: Relationship back to the Buyer object.
    :vartype user: relationship
    :ivar screening: Relationship back to the Screening object.
    :vartype screening: relationship
    :ivar booked_seats: Relationship to the :class:`BookedSeat` mapping the seats included in this booking.
    :vartype booked_seats: relationship
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
    Mapping table between a :class:`Booking` and the individual :class:`ShowSeat` confirmed.
    Ensures a single ShowSeat record can only be part of one final Booking.

    :ivar id: Primary key for the mapping record.
    :vartype id: int
    :ivar booking_id: Foreign key to the parent :class:`Booking` record.
    :vartype booking_id: int
    :ivar show_seat_id: Foreign key to the :class:`ShowSeat` record that was confirmed. Must be unique per booking.
    :vartype show_seat_id: int
    :ivar booking: Relationship back to the parent :class:`Booking` object.
    :vartype booking: relationship
    :ivar show_seat: Relationship to the :class:`ShowSeat` object that was booked.
    :vartype show_seat: relationship
    """
    __tablename__ = "bookingseat" # FIX: Correct schema table name
    
    id = Column(Integer, primary_key=True, index=True) # Retaining simple PK for SQLAlchemy model ease
    
    # FIX: Foreign Key references the 'bookingid' primary key on the booking table
    booking_id = Column(Integer, ForeignKey("booking.bookingid"), nullable=False) 
    show_seat_id = Column(Integer, ForeignKey("show_seat.id"), nullable=False, unique=True)
    
    booking = relationship("Booking", back_populates="booked_seats", foreign_keys=[booking_id])
    show_seat = relationship("ShowSeat", foreign_keys=[show_seat_id])