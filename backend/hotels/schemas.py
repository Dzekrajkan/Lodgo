from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class FacilitiesCreate(BaseModel):
    name: str

class FacilityOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class ServiceCreate(BaseModel):
    hotel_id: int
    name: str
    price: int

class ServiceOut(BaseModel):
    id: int
    hotel_id: int
    name: str
    price: int

    model_config = ConfigDict(from_attributes=True)

class RoomCreate(BaseModel):
    hotel_id: int
    name: str
    description: str
    price_per_night: int
    capacity: int
    quantity: int

class RoomOut(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: str
    price_per_night: int
    capacity: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)

class RoomAvailabilityOut(RoomOut):
    available: int

class HotelImageOut(BaseModel):
    id: int
    image_url: str
    is_main: bool

    model_config = ConfigDict(from_attributes=True)

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
    rating: float = 0.0
    reviews_count: Optional[int] = 0
    check_in_time: str
    check_out_time: str
    facilities: list[FacilityOut] = []
    images: list[HotelImageOut] = []
    services: list[ServiceOut] = []

    model_config = ConfigDict(from_attributes=True)

class FavoriteHotelCreate(BaseModel):
    hotel_id: int

class FavoriteHotelOut(BaseModel):
    id: int
    created_at: datetime
    hotel: HotelOut

    model_config = ConfigDict(from_attributes=True)