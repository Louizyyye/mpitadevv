
# EOF
"""
app/schemas.py

Pydantic (v2) schemas for Mpita Medical.
Uses `model_config = ConfigDict(from_attributes=True)` so ORM objects are accepted.
"""

from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict
from typing import Optional, List
from datetime import datetime, date
import enum


# ----------------- ENUMS -----------------
class UserRole(str, enum.Enum):
    PATIENT = "patient"
    ADMIN = "admin"


class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    MPESA = "mpesa"
    AIRTEL = "airtel"
    BANK = "bank"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class NotificationType(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ALERT = "alert"


class LogLevel(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


# ----------------- USER SCHEMAS -----------------
class UserBase(BaseModel):
    name: str = Field(..., example="John Doe")
    email: EmailStr = Field(..., example="johndoe@example.com")
    phone: Optional[str] = Field(None, example="+254700000000")
    occupation: Optional[str] = Field(None, example="Teacher")
    role: UserRole = Field(UserRole.PATIENT, example="patient")
    is_active: Optional[bool] = Field(True, example=True)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, example="strong_password_123")


class UserUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    occupation: Optional[str]
    role: Optional[UserRole]
    is_active: Optional[bool]


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------- PAYMENT SCHEMAS -----------------
class PaymentBase(BaseModel):
    method: PaymentMethod = Field(..., example="mpesa")
    transaction_code: Optional[str] = Field(None, example="MPESA12345")
    amount: float = Field(..., gt=0, example=2500.0)
    status: PaymentStatus = Field(PaymentStatus.PENDING, example="pending")
    phone_number: Optional[str] = Field(None, example="+254700000000")
    description: Optional[str] = Field(None, example="Consultation fee")


class PaymentCreate(PaymentBase):
    appointment_id: Optional[int] = Field(None, description="Linked appointment id")
    user_id: Optional[int] = Field(None, description="Paying user id")


class PaymentResponse(PaymentBase):
    id: int
    user_id: int
    appointment_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------- APPOINTMENT SCHEMAS -----------------
class AppointmentBase(BaseModel):
    user_id: int = Field(..., description="ID of the patient")
    specialist: str = Field(..., example="Cardiologist")
    service_type: str = Field(..., example="Consultation")
    appointment_date: datetime = Field(..., description="Date/time of appointment")
    status: AppointmentStatus = Field(AppointmentStatus.PENDING, example="pending")
    notes: Optional[str] = Field(None, example="Patient has chest pain")


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    specialist: Optional[str]
    service_type: Optional[str]
    appointment_date: Optional[datetime]
    status: Optional[AppointmentStatus]
    notes: Optional[str]


class AppointmentResponse(AppointmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # optionally include a single payment summary (if present)
    payment: Optional[PaymentResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ----------------- NOTIFICATION SCHEMAS -----------------
class NotificationBase(BaseModel):
    user_id: int
    type: NotificationType = Field(NotificationType.INFO)
    message: str


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------- LOG SCHEMAS -----------------
class LogBase(BaseModel):
    user_id: Optional[int] = None
    level: LogLevel = Field(LogLevel.INFO)
    message: str


class LogCreate(LogBase):
    pass


class LogResponse(LogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------- NESTED / COMPOSITE SCHEMAS -----------------
class AppointmentWithPayments(AppointmentResponse):
    payments: List[PaymentResponse] = []


class UserWithAppointments(UserResponse):
    appointments: List[AppointmentWithPayments] = []


# ----------------- Convenience response types -----------------
class MessageResponse(BaseModel):
    message: str

