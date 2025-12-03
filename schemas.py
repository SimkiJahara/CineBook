from typing import Optional, List
from datetime import date, datetime, time
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class UserBase(BaseModel):
    email: str
    name: str
    role: str  # 'TheatreOwner', 'Buyer', 'Superadmin', 'TheaterOwner'


class UserCreate(UserBase):
    passwordhash: str


class User(UserBase):
    id: int
    passwordhash: str

    model_config = ConfigDict(from_attributes=True)


class BuyerBase(BaseModel):
    fullname: str


class BuyerCreate(UserCreate, BuyerBase):
    pass


class Buyer(User, BuyerBase):
    booking: Optional[List["Booking"]] = []

    model_config = ConfigDict(from_attributes=True)


class SuperadminBase(BaseModel):
    pass


class SuperadminCreate(UserCreate, SuperadminBase):
    pass


class Superadmin(User, SuperadminBase):
    promocode: Optional[List["Promocode"]] = []

    model_config = ConfigDict(from_attributes=True)


class TheaterownerBase(BaseModel):
    businessname: str
    ownername: str
    phone: Optional[str] = None
    licensenumber: Optional[str] = None
    bankdetails: Optional[dict] = None
    logourl: Optional[str] = None


class TheaterownerCreate(UserCreate, TheaterownerBase):
    pass


class Theaterowner(User, TheaterownerBase):
    screeningdraft: Optional[List["Screeningdraft"]] = []
    theater: Optional[List["Theater"]] = []

    model_config = ConfigDict(from_attributes=True)


class GenresBase(BaseModel):
    name: str
    description: Optional[str] = None


class GenresCreate(GenresBase):
    pass


class Genres(GenresBase):
    id: int
    created_at: Optional[datetime] = None
    movie: Optional[List["Movie"]] = []

    model_config = ConfigDict(from_attributes=True)


class MovieBase(BaseModel):
    eidr: str
    title: str
    posterurl: Optional[str] = None
    lengthmin: Optional[int] = None
    rating: Optional[str] = None
    releasedate: Optional[date] = None
    description: Optional[str] = None
    director: Optional[str] = None
    trailerurl: Optional[str] = None
    language: Optional[str] = "English"
    is_active: Optional[int] = 1


class MovieCreate(MovieBase):
    pass


class Movie(MovieBase):
    created_at: Optional[datetime] = None
    genre: Optional[List[Genres]] = []
    movie_cast: Optional[List["MovieCast"]] = []
    reviews: Optional[List["Reviews"]] = []
    screening: Optional[List["Screening"]] = []

    model_config = ConfigDict(from_attributes=True)


class MovieCastBase(BaseModel):
    cast_member: str
    movie_eidr: Optional[str] = None


class MovieCastCreate(MovieCastBase):
    pass


class MovieCast(MovieCastBase):
    id: int
    movie: Optional[Movie] = None

    model_config = ConfigDict(from_attributes=True)


class ReviewsBase(BaseModel):
    movie_eidr: Optional[str] = None
    user_id: Optional[int] = None
    rating: Optional[Decimal] = None
    review_text: Optional[str] = None


class ReviewsCreate(ReviewsBase):
    pass


class Reviews(ReviewsBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    movie: Optional[Movie] = None
    user: Optional[User] = None

    model_config = ConfigDict(from_attributes=True)


class PromocodeBase(BaseModel):
    code: str
    discountvalue: Decimal
    discounttype: str
    validfrom: datetime
    validto: datetime
    applied_to: Decimal = Decimal("1.0")
    createdbyadminid: int
    maxuses: Optional[int] = None
    currentusecount: Optional[int] = 0
    scope: Optional[str] = None


class PromocodeCreate(PromocodeBase):
    pass


class Promocode(PromocodeBase):
    superadmin: Optional[Superadmin] = None
    booking: Optional[List["Booking"]] = []

    model_config = ConfigDict(from_attributes=True)


class ScreeningdraftBase(BaseModel):
    ownerid: int
    draftdata: Optional[dict] = None


class ScreeningdraftCreate(ScreeningdraftBase):
    pass


class Screeningdraft(ScreeningdraftBase):
    id: int
    createdat: Optional[datetime] = None
    theaterowner: Optional[Theaterowner] = None

    model_config = ConfigDict(from_attributes=True)


class TheaterBase(BaseModel):
    companyid: str
    branchid: str
    name: str
    address: str
    ownerid: int
    contact: Optional[str] = None
    logourl: Optional[str] = None
    isverified: Optional[bool] = False


class TheaterCreate(TheaterBase):
    pass


class Theater(TheaterBase):
    theaterowner: Optional[Theaterowner] = None
    hall: Optional[List["Hall"]] = []

    model_config = ConfigDict(from_attributes=True)


class HallBase(BaseModel):
    hallid: str
    companyid: str
    branchid: str
    capacity: int


class HallCreate(HallBase):
    pass


class Hall(HallBase):
    theater: Optional[Theater] = None
    screening: Optional[List["Screening"]] = []

    model_config = ConfigDict(from_attributes=True)


class ScreeningBase(BaseModel):
    date: date
    starttime: time
    status: str = "SCHEDULED"
    movieeidr: str
    hallid: str
    hallcompanyid: str
    hallbranchid: str


class ScreeningCreate(ScreeningBase):
    pass


class Screening(ScreeningBase):
    id: int
    hall: Optional[Hall] = None
    movie: Optional[Movie] = None
    booking: Optional[List["Booking"]] = []

    model_config = ConfigDict(from_attributes=True)


class SeatlayoutBase(BaseModel):
    layouthallid: str
    layoutcompanyid: str
    layoutbranchid: str
    # Inherited from Hall
    capacity: int


class SeatlayoutCreate(SeatlayoutBase):
    pass


class Seatlayout(SeatlayoutBase):
    # Hall fields (since Seatlayout inherits from Hall in ORM)
    hallid: str
    companyid: str
    branchid: str
    seat: Optional[List["Seat"]] = []

    model_config = ConfigDict(from_attributes=True)


class SeatBase(BaseModel):
    seatid: str
    layouthallid: str
    layoutcompanyid: str
    layoutbranchid: str
    rownumber: str
    number: int
    type: Optional[str] = None
    status: Optional[str] = "AVAILABLE"


class SeatCreate(SeatBase):
    pass


class Seat(SeatBase):
    booking: Optional[List["Booking"]] = []
    seatlayout: Optional[Seatlayout] = None

    model_config = ConfigDict(from_attributes=True)


class BookingBase(BaseModel):
    totalamount: Decimal
    paymentmethod: str
    status: str = "PENDING"
    buyerid: int
    screeningid: int
    qrcodeurl: Optional[str] = None
    promocode: Optional[str] = None


class BookingCreate(BookingBase):
    pass


class Booking(BookingBase):
    bookingid: int
    bookedat: Optional[datetime] = None
    buyer: Optional[Buyer] = None
    promocode_: Optional[Promocode] = None
    screening: Optional[Screening] = None
    seat: Optional[List[Seat]] = []

    model_config = ConfigDict(from_attributes=True)


# Update forward references
Buyer.model_rebuild()
Superadmin.model_rebuild()
Theaterowner.model_rebuild()
Genres.model_rebuild()
Movie.model_rebuild()
MovieCast.model_rebuild()
Reviews.model_rebuild()
Promocode.model_rebuild()
Screeningdraft.model_rebuild()
Theater.model_rebuild()
Hall.model_rebuild()
Screening.model_rebuild()
Seatlayout.model_rebuild()
Booking.model_rebuild()
Seat.model_rebuild()
