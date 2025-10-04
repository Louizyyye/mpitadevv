from pydantic import BaseModel, EmailStr
from app.models import UserRole
from typing import Optional
from datetime import datetime

# --- Schemas for Users ---
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    occupation: Optional[str] = None
    role: UserRole = UserRole.PATIENT
    is_active: bool = True

class UserCreate(UserBase):
    password: str  # Plain password input for creation

class UserUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    occupation: Optional[str]
    role: Optional[UserRole]
    is_active: Optional[bool]

class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 replacement for orm_mode
