from typing import Optional
import datetime
import decimal

from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, Time, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'User'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='User_pkey'),
        UniqueConstraint('email', name='User_email_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    passwordhash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(Enum('TheatreOwner', 'Buyer', 'Superadmin', 'TheaterOwner', name='userrole'), nullable=False)

    reviews: Mapped[list['Reviews']] = relationship('Reviews', back_populates='user')


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


class Buyer(User):
    __tablename__ = 'buyer'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['User.id'], name='buyer_id_fkey'),
        PrimaryKeyConstraint('id', name='buyer_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fullname: Mapped[str] = mapped_column(String(255), nullable=False)

    booking: Mapped[list['Booking']] = relationship('Booking', back_populates='buyer')


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


class Superadmin(User):
    __tablename__ = 'superadmin'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['User.id'], name='superadmin_id_fkey'),
        PrimaryKeyConstraint('id', name='superadmin_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    promocode: Mapped[list['Promocode']] = relationship('Promocode', back_populates='superadmin')


class Theaterowner(User):
    __tablename__ = 'theaterowner'
    __table_args__ = (
        ForeignKeyConstraint(['id'], ['User.id'], name='theaterowner_id_fkey'),
        PrimaryKeyConstraint('id', name='theaterowner_pkey'),
        UniqueConstraint('businessname', name='theaterowner_businessname_key'),
        UniqueConstraint('licensenumber', name='theaterowner_licensenumber_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    businessname: Mapped[str] = mapped_column(String(255), nullable=False)
    ownername: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    licensenumber: Mapped[Optional[str]] = mapped_column(String(100))
    bankdetails: Mapped[Optional[dict]] = mapped_column(JSONB)
    logourl: Mapped[Optional[str]] = mapped_column(String(255))

    screeningdraft: Mapped[list['Screeningdraft']] = relationship('Screeningdraft', back_populates='theaterowner')
    theater: Mapped[list['Theater']] = relationship('Theater', back_populates='theaterowner')


class Promocode(Base):
    __tablename__ = 'promocode'
    __table_args__ = (
        ForeignKeyConstraint(['createdbyadminid'], ['superadmin.id'], name='promocode_createdbyadminid_fkey'),
        PrimaryKeyConstraint('code', name='promocode_pkey')
    )

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    discountvalue: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    discounttype: Mapped[str] = mapped_column(String(50), nullable=False)
    validfrom: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    validto: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    applied_to: Mapped[decimal.Decimal] = mapped_column(Numeric(3, 2), nullable=False, server_default=text('1.0'))
    createdbyadminid: Mapped[int] = mapped_column(Integer, nullable=False)
    maxuses: Mapped[Optional[int]] = mapped_column(Integer)
    currentusecount: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    scope: Mapped[Optional[str]] = mapped_column(String(50))

    superadmin: Mapped['Superadmin'] = relationship('Superadmin', back_populates='promocode')
    booking: Mapped[list['Booking']] = relationship('Booking', back_populates='promocode_')


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


class Theater(Base):
    __tablename__ = 'theater'
    __table_args__ = (
        ForeignKeyConstraint(['ownerid'], ['theaterowner.id'], name='theater_ownerid_fkey'),
        PrimaryKeyConstraint('companyid', 'branchid', name='theater_pkey')
    )

    companyid: Mapped[str] = mapped_column(String(50), primary_key=True)
    branchid: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    ownerid: Mapped[int] = mapped_column(Integer, nullable=False)
    contact: Mapped[Optional[str]] = mapped_column(String(20))
    logourl: Mapped[Optional[str]] = mapped_column(String(255))
    isverified: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))

    theaterowner: Mapped['Theaterowner'] = relationship('Theaterowner', back_populates='theater')
    hall: Mapped[list['Hall']] = relationship('Hall', back_populates='theater')


class Hall(Base):
    __tablename__ = 'hall'
    __table_args__ = (
        ForeignKeyConstraint(['companyid', 'branchid'], ['theater.companyid', 'theater.branchid'], name='hall_companyid_branchid_fkey'),
        PrimaryKeyConstraint('hallid', 'companyid', 'branchid', name='hall_pkey')
    )

    hallid: Mapped[str] = mapped_column(String(50), primary_key=True)
    companyid: Mapped[str] = mapped_column(String(50), primary_key=True)
    branchid: Mapped[str] = mapped_column(String(50), primary_key=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    theater: Mapped['Theater'] = relationship('Theater', back_populates='hall')
    screening: Mapped[list['Screening']] = relationship('Screening', back_populates='hall')


class Screening(Base):
    __tablename__ = 'screening'
    __table_args__ = (
        ForeignKeyConstraint(['hallid', 'hallcompanyid', 'hallbranchid'], ['hall.hallid', 'hall.companyid', 'hall.branchid'], name='screening_hallid_hallcompanyid_hallbranchid_fkey'),
        ForeignKeyConstraint(['movieeidr'], ['movie.eidr'], name='screening_movieeidr_fkey'),
        PrimaryKeyConstraint('id', name='screening_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    starttime: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'SCHEDULED'::character varying"))
    movieeidr: Mapped[str] = mapped_column(String(50), nullable=False)
    hallid: Mapped[str] = mapped_column(String(50), nullable=False)
    hallcompanyid: Mapped[str] = mapped_column(String(50), nullable=False)
    hallbranchid: Mapped[str] = mapped_column(String(50), nullable=False)

    hall: Mapped['Hall'] = relationship('Hall', back_populates='screening')
    movie: Mapped['Movie'] = relationship('Movie', back_populates='screening')
    booking: Mapped[list['Booking']] = relationship('Booking', back_populates='screening')


class Seatlayout(Hall):
    __tablename__ = 'seatlayout'
    __table_args__ = (
        ForeignKeyConstraint(['layouthallid', 'layoutcompanyid', 'layoutbranchid'], ['hall.hallid', 'hall.companyid', 'hall.branchid'], name='seatlayout_layouthallid_layoutcompanyid_layoutbranchid_fkey'),
        PrimaryKeyConstraint('layouthallid', 'layoutcompanyid', 'layoutbranchid', name='seatlayout_pkey')
    )

    layouthallid: Mapped[str] = mapped_column(String(50), primary_key=True)
    layoutcompanyid: Mapped[str] = mapped_column(String(50), primary_key=True)
    layoutbranchid: Mapped[str] = mapped_column(String(50), primary_key=True)

    seat: Mapped[list['Seat']] = relationship('Seat', back_populates='seatlayout')


class Booking(Base):
    __tablename__ = 'booking'
    __table_args__ = (
        ForeignKeyConstraint(['buyerid'], ['buyer.id'], name='booking_buyerid_fkey'),
        ForeignKeyConstraint(['promocode'], ['promocode.code'], name='booking_promocode_fkey'),
        ForeignKeyConstraint(['screeningid'], ['screening.id'], name='booking_screeningid_fkey'),
        PrimaryKeyConstraint('bookingid', name='booking_pkey')
    )

    bookingid: Mapped[int] = mapped_column(Integer, primary_key=True)
    totalamount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    paymentmethod: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'PENDING'::character varying"))
    buyerid: Mapped[int] = mapped_column(Integer, nullable=False)
    screeningid: Mapped[int] = mapped_column(Integer, nullable=False)
    qrcodeurl: Mapped[Optional[str]] = mapped_column(String(255))
    bookedat: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    promocode: Mapped[Optional[str]] = mapped_column(String(50))

    buyer: Mapped['Buyer'] = relationship('Buyer', back_populates='booking')
    promocode_: Mapped[Optional['Promocode']] = relationship('Promocode', back_populates='booking')
    screening: Mapped['Screening'] = relationship('Screening', back_populates='booking')
    seat: Mapped[list['Seat']] = relationship('Seat', secondary='bookingseat', back_populates='booking')


class Seat(Base):
    __tablename__ = 'seat'
    __table_args__ = (
        ForeignKeyConstraint(['layouthallid', 'layoutcompanyid', 'layoutbranchid'], ['seatlayout.layouthallid', 'seatlayout.layoutcompanyid', 'seatlayout.layoutbranchid'], name='seat_layouthallid_layoutcompanyid_layoutbranchid_fkey'),
        PrimaryKeyConstraint('seatid', 'layouthallid', 'layoutcompanyid', 'layoutbranchid', name='seat_pkey')
    )

    seatid: Mapped[str] = mapped_column(String(50), primary_key=True)
    layouthallid: Mapped[str] = mapped_column(String(50), primary_key=True)
    layoutcompanyid: Mapped[str] = mapped_column(String(50), primary_key=True)
    layoutbranchid: Mapped[str] = mapped_column(String(50), primary_key=True)
    rownumber: Mapped[str] = mapped_column(String(10), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'AVAILABLE'::character varying"))

    booking: Mapped[list['Booking']] = relationship('Booking', secondary='bookingseat', back_populates='seat')
    seatlayout: Mapped['Seatlayout'] = relationship('Seatlayout', back_populates='seat')


t_bookingseat = Table(
    'bookingseat', Base.metadata,
    Column('bookingid', Integer, primary_key=True),
    Column('seatid', String(50), primary_key=True),
    Column('seatlayouthallid', String(50), primary_key=True),
    Column('seatlayoutcompanyid', String(50), primary_key=True),
    Column('seatlayoutbranchid', String(50), primary_key=True),
    ForeignKeyConstraint(['bookingid'], ['booking.bookingid'], name='bookingseat_bookingid_fkey'),
    ForeignKeyConstraint(['seatid', 'seatlayouthallid', 'seatlayoutcompanyid', 'seatlayoutbranchid'], ['seat.seatid', 'seat.layouthallid', 'seat.layoutcompanyid', 'seat.layoutbranchid'], name='bookingseat_seatid_seatlayouthallid_seatlayoutcompanyid_se_fkey'),
    PrimaryKeyConstraint('bookingid', 'seatid', 'seatlayouthallid', 'seatlayoutcompanyid', 'seatlayoutbranchid', name='bookingseat_pkey')
)
