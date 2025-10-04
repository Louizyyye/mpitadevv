# app/schemas/payments.py

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


# ==========================================================
#                     PAYMENT SCHEMAS
# ==========================================================

class PaymentBase(BaseModel):
    appointment_id: Optional[int] = Field(None, description="Linked appointment ID")
    user_id: Optional[int] = Field(None, description="User making the payment")
    amount: float = Field(..., gt=0, description="Payment amount")
    method: str = Field(..., description="Payment method (e.g. MPESA, Airtel, Bank)")
    status: str = Field(default="pending", description="pending | completed | failed | refunded")
    phone_number: Optional[str] = Field(None, description="Phone number used for payment")
    description: Optional[str] = Field(None, description="Payment description or notes")


class PaymentCreate(PaymentBase):
    """Schema for creating a new payment"""
    appointment_id: int = Field(..., description="Appointment ID for the payment")
    amount: float = Field(..., gt=0, description="Payment amount")
    method: str = Field(..., description="Payment method used")


class PaymentUpdate(BaseModel):
    """Schema for updating an existing payment"""
    amount: Optional[float] = Field(None, gt=0)
    status: Optional[str] = Field(None, description="pending | completed | failed | refunded")
    method: Optional[str] = None
    phone_number: Optional[str] = None
    description: Optional[str] = None


class PaymentResponse(PaymentBase):
    """Schema for returning payment data"""
    id: int
    user_id: Optional[int]
    appointment_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# ==========================================================
#             NESTED RELATIONSHIPS (OPTIONAL)
# ==========================================================

class AppointmentWithPayments(BaseModel):
    """Include payments within an appointment response"""
    id: int
    status: str
    appointment_date: datetime
    payments: List[PaymentResponse] = []

    model_config = ConfigDict(from_attributes=True)
