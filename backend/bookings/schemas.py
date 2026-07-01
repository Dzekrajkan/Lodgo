from datetime import date, datetime
from typing import List
from pydantic import BaseModel, ConfigDict
from backend.hotels.schemas import HotelOut, RoomOut
from backend.models import BookingStatus

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
    status: BookingStatus
    date_from: date
    date_to: date
    created_at: datetime
    hotel: HotelOut
    room: RoomOut

    model_config = ConfigDict(from_attributes=True)

class BookingStatusOut(BaseModel):
    id: int
    user_id: int
    room_id: int
    hotel_id: int
    total_price: int
    status: BookingStatus
    date_from: date
    date_to: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)