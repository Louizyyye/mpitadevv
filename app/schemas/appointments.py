from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date as DateType
from typing import Optional, List
from app.schemas.payments import PaymentResponse

# ==========================================================
#                     APPOINTMENT SCHEMAS
# ==========================================================

class AppointmentBase(BaseModel):
    """
    Base schema for appointment creation and updates.
    """
    user_id: int = Field(..., description="ID of the user booking the appointment")
    specialist: str = Field(..., description="Doctor or specialist assigned")
    service_type: str = Field(..., description="Type of service / consultation")
    appointment_date: DateType = Field(..., description="Date of the appointment")
    notes: Optional[str] = Field(None, description="Optional notes about the appointment")


class AppointmentCreate(AppointmentBase):
    """
    Schema used when creating a new appointment.
    """
    pass  # Inherits all required fields from AppointmentBase


class AppointmentUpdate(BaseModel):
    """
    Schema for updating an appointment (partial update).
    """
    specialist: Optional[str] = None
    service_type: Optional[str] = None
    appointment_date: Optional[DateType] = None
    notes: Optional[str] = None
    status: Optional[str] = Field(None, description="pending | confirmed | completed | cancelled")


class AppointmentResponse(AppointmentBase):
    """
    Schema returned for appointment queries.
    """
    id: int
    status: str = "pending"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================================
#              NESTED RELATIONSHIPS (OPTIONAL)
# ==========================================================

class AppointmentWithPayments(AppointmentResponse):
    """
    Optional nested schema for an appointment including related payments.
    """
    payments: List[PaymentResponse] = []
