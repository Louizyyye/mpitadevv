"""
Database models for Mpita Medical Platform.
Includes Users, Appointments, Payments, Notifications, and Logs.
Compatible with PostgreSQL (psycopg3) and Render deployment.
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Index, Boolean
)
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from datetime import datetime
import enum

from app.database import Base


# ============================================================
# ENUM DEFINITIONS
# ============================================================

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


# ============================================================
# DATABASE MODELS
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    occupation = Column(String(100), nullable=True)
    national_id = Column(String(20), nullable=True)
    otp = Column(String(10), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.PATIENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_email_phone", "email", "phone"),
        Index("idx_user_active", "is_active"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "occupation": self.occupation,
            "national_id": self.national_id,
            "otp": self.otp,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    specialist = Column(String(100), nullable=False)
    service_type = Column(String(100), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="appointments")
    payment = relationship("Payment", back_populates="appointment", uselist=False)

    __table_args__ = (
        Index("idx_user_appointment", "user_id", "appointment_date"),
        Index("idx_specialist_date", "specialist", "appointment_date"),
        Index("idx_status", "status"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "specialist": self.specialist,
            "service_type": self.service_type,
            "appointment_date": self.appointment_date.isoformat(),
            "status": self.status.value,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="CASCADE"), nullable=True)
    method = Column(Enum(PaymentMethod), nullable=False)
    transaction_code = Column(String(100), unique=True, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    phone_number = Column(String(20), nullable=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="payments")
    appointment = relationship("Appointment", back_populates="payment")

    __table_args__ = (
        Index("idx_user_payment", "user_id", "created_at"),
        Index("idx_transaction_code", "transaction_code"),
        Index("idx_payment_status", "status"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "appointment_id": self.appointment_id,
            "method": self.method.value,
            "transaction_code": self.transaction_code,
            "amount": self.amount,
            "status": self.status.value,
            "phone_number": self.phone_number,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(NotificationType), default=NotificationType.INFO, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="notifications")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type.value,
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat()
        }


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    level = Column(Enum(LogLevel), default=LogLevel.INFO, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="logs")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "level": self.level.value,
            "message": self.message,
            "created_at": self.created_at.isoformat()
        }


# ============================================================
# PYDANTIC SCHEMAS
# ============================================================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    occupation: str | None = None
    password: str
    role: UserRole = UserRole.PATIENT


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    occupation: str | None = None
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
