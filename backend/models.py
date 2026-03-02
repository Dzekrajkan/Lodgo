from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func, UniqueConstraint, Enum, Table
from sqlalchemy.orm import relationship
import enum
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    hotels = relationship("Hotel", back_populates="owner")
    bookings = relationship("Booking", back_populates="user")
    favorite_hotels = relationship("FavoriteHotel", back_populates="user")

hotel_facilities = Table(
    "hotel_facilities",
    Base.metadata,
    Column("hotel_id", ForeignKey("hotels.id"), primary_key=True),
    Column("facility_id", ForeignKey("facilities.id"), primary_key=True),
)

booking_services = Table(
    "booking_services",
    Base.metadata,
    Column("booking_id", ForeignKey("bookings.id"), primary_key=True),
    Column("service_id", ForeignKey("services.id"), primary_key=True),
)

class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)

    address = Column(String, nullable=False)
    city = Column(String, index=True, nullable=False)
    country = Column(String, index=True, nullable=False)

    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)

    price_per_night = Column(Integer, nullable=False)

    check_in_time = Column(String, default="14:00")
    check_out_time = Column(String, default="12:00")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="hotels")
    rooms = relationship("Room", back_populates="hotel", cascade="all, delete")
    images = relationship("HotelImage", back_populates="hotel", cascade="all, delete")
    bookings = relationship("Booking", back_populates="hotel")
    facilities = relationship("Facility", secondary=hotel_facilities, back_populates="hotels")
    favorited_by = relationship("FavoriteHotel", back_populates="hotel")
    services = relationship("Service", back_populates="hotels")
    reviews = relationship("Review", back_populates="hotel", cascade="all, delete")

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    price_per_night = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)

    hotel = relationship("Hotel", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")

class BookingStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)

    guest_first_name = Column(String, nullable=False)
    guest_last_name = Column(String, nullable=False)
    guest_email = Column(String, nullable=False)

    date_from = Column(DateTime, nullable=False)
    date_to = Column(DateTime, nullable=False)

    total_price = Column(Integer, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.pending)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="bookings")
    hotel = relationship("Hotel", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    services = relationship("Service",secondary=booking_services,backref="bookings")

class HotelImage(Base):
    __tablename__ = "hotel_images"

    id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)

    image_url = Column(String, nullable=False)
    is_main = Column(Boolean, default=False)

    hotel = relationship("Hotel", back_populates="images")

class Facility(Base):
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    hotels = relationship(
        "Hotel",
        secondary=hotel_facilities,
        back_populates="facilities",
    )

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    name = Column(String, unique=True, nullable=False)
    price = Column(Integer, nullable=False)

    hotels = relationship("Hotel", back_populates="services")

class FavoriteHotel(Base):
    __tablename__ = "favorite_hotels"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="favorite_hotels")
    hotel = relationship("Hotel", back_populates="favorited_by")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)

    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    hotel = relationship("Hotel", back_populates="reviews")
    booking = relationship("Booking")

    __table_args__ = (
        UniqueConstraint("booking_id", name="unique_review_per_booking"),
    )
