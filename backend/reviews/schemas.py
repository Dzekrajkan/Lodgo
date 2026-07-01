from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from backend.auth.schemas import UserOut

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

    model_config = ConfigDict(from_attributes=True)