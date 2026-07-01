from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password1: str
    password2: str
    is_verified: Optional[bool] = False

    @field_validator("password2")
    def passwords_match(cls, v, info):
        if info.data.get("password1") != v:
            raise ValueError("The passwords don't match")
        return v

class UserOut(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)

class UserMeOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)