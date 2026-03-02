from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, Literal, List
from datetime import datetime, date

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password1: str
    password2: str
    is_verified: Optional[bool] = False

    @validator('password2')
    def passwords_match(cls, v, values):
        if 'password1' in values and v != values['password1']:
            raise ValueError("The passwords don't match")
        return v

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True
    
class FacilitiesCreate(BaseModel):
    name: str
    
class FacilityOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class ServiceCreate(BaseModel):
    hotel_id: int
    name: str
    price: int

class ServiceOut(BaseModel):
    id: int
    hotel_id: int
    name: str
    price: int

    class Config:
        from_attributes = True

class RoomCreate(BaseModel):
    hotel_id: int
    name: str
    description: str
    price_per_night: int
    capacity: int
    quantity: int

class RoomOut(BaseModel):
    id: int
    name: str
    description: str
    price_per_night: int
    capacity: int
    quantity: int

class HotelImageOut(BaseModel):
    id: int
    image_url: str
    is_main: bool

    class Config:
        from_attributes = True

class HotelCreate(BaseModel):
    name: str
    owner_id: int
    description: Optional[str] = None
    address: str
    city: str
    country: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    price_per_night: int
    check_in_time: Optional[str] = "14:00"
    check_out_time: Optional[str] = "12:00"
    facility_ids: List[int] = []
    service_ids: List[int] = []

class HotelOut(BaseModel):
    id: int
    owner_id: int
    name: str
    description: str
    address: str
    city: str
    country: str
    latitude: str
    longitude: str
    price_per_night: int
    rating: float
    reviews_count: Optional[int] = 0
    check_in_time: str
    check_out_time: str
    facilities: list[FacilityOut] = []
    images: list[HotelImageOut] = []
    services: list[ServiceOut] = []

    class Config:
        from_attributes = True

class BookingsCreate(BaseModel):
    room_id: int
    hotel_id: int
    date_from: date
    date_to: date
    guest_first_name: str
    guest_last_name: str
    guest_email: str
    service_ids: List[int] = []

class BookingsPay(BaseModel):
    id: int
    username: str
    card_number: str
    card_expiration_date: str
    CVC: str

class BookingsOut(BaseModel):
    id: int
    user_id: int
    total_price: int
    status: str
    date_from: date
    date_to: date
    created_at: date
    hotel: HotelOut
    room: RoomOut

class FavoriteHotelCreate(BaseModel):
    hotel_id: int

class ReviewCreate(BaseModel):
    hotel_id: int
    booking_id: Optional[int] = None
    rating: int
    comment: str

class ReviewOut(BaseModel):
    id: int
    user_id: int
    hotel_id: int
    booking_id: int
    rating: int
    comment: str
    created_at: datetime
    user: UserOut

    class Config:
        from_attributes = True