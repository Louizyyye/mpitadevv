
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Appointment, AppointmentStatus, User
from app.utils.auth import get_current_user

router = APIRouter()

# Available specialists and services (can be moved to database later)
SPECIALISTS = [
    "General Practitioner",
    "Cardiologist",
    "Dentist",
    "Dermatologist",
    "Gynecologist",
    "Pediatrician",
    "Psychiatrist",
    "Orthopedist",
    "Ophthalmologist",
    "ENT Specialist"
]

SERVICE_TYPES = [
    "Consultation",
    "Follow-up",
    "Emergency",
    "Surgery",
    "Laboratory Test",
    "X-Ray",
    "Ultrasound",
    "Vaccination",
    "Physical Therapy",
    "Mental Health Session"
]


# Pydantic schemas
class AppointmentCreate(BaseModel):
    specialist: str
    service_type: str
    appointment_date: datetime
    notes: Optional[str] = Field(None, max_length=500)

    @validator('specialist')
    def validate_specialist(cls, v):
        if v not in SPECIALISTS:
            raise ValueError(f'Specialist must be one of: {", ".join(SPECIALISTS)}')
        return v

    @validator('service_type')
    def validate_service_type(cls, v):
        if v not in SERVICE_TYPES:
            raise ValueError(f'Service type must be one of: {", ".join(SERVICE_TYPES)}')
        return v

    @validator('appointment_date')
    def validate_date(cls, v):
        if v < datetime.now():
            raise ValueError('Appointment date cannot be in the past')
        if v > datetime.now() + timedelta(days=90):
            raise ValueError('Appointment cannot be scheduled more than 90 days in advance')
        return v


class AppointmentUpdate(BaseModel):
    specialist: Optional[str] = None
    service_type: Optional[str] = None
    appointment_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
    status: Optional[AppointmentStatus] = None

    @validator('specialist')
    def validate_specialist(cls, v):
        if v and v not in SPECIALISTS:
            raise ValueError(f'Specialist must be one of: {", ".join(SPECIALISTS)}')
        return v

    @validator('service_type')
    def validate_service_type(cls, v):
        if v and v not in SERVICE_TYPES:
            raise ValueError(f'Service type must be one of: {", ".join(SERVICE_TYPES)}')
        return v

    @validator('appointment_date')
    def validate_date(cls, v):
        if v and v < datetime.now():
            raise ValueError('Appointment date cannot be in the past')
        return v


@router.get("/specialists")
async def get_specialists():
    """Get list of available specialists"""
    return {
        "success": True,
        "data": SPECIALISTS
    }


@router.get("/services")
async def get_services():
    """Get list of available service types"""
    return {
        "success": True,
        "data": SERVICE_TYPES
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_appointment(
        appointment_data: AppointmentCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Create a new appointment"""
    # Check if user already has an appointment at the same time
    existing_appointment = db.query(Appointment).filter(
        and_(
            Appointment.user_id == current_user.id,
            Appointment.appointment_date == appointment_data.appointment_date,
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
        )
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an appointment at this time"
        )

    # Create new appointment
    new_appointment = Appointment(
        user_id=current_user.id,
        specialist=appointment_data.specialist,
        service_type=appointment_data.service_type,
        appointment_date=appointment_data.appointment_date,
        notes=appointment_data.notes,
        status=AppointmentStatus.PENDING
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return {
        "success": True,
        "message": "Appointment created successfully. Please complete payment to confirm.",
        "data": new_appointment.to_dict()
    }


@router.get("/")
async def get_appointments(
        status_filter: Optional[AppointmentStatus] = Query(None),
        specialist: Optional[str] = Query(None),
        from_date: Optional[datetime] = Query(None),
        to_date: Optional[datetime] = Query(None),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get user's appointments with optional filters"""
    query = db.query(Appointment).filter(Appointment.user_id == current_user.id)

    if status_filter:
        query = query.filter(Appointment.status == status_filter)

    if specialist:
        query = query.filter(Appointment.specialist == specialist)

    if from_date:
        query = query.filter(Appointment.appointment_date >= from_date)

    if to_date:
        query = query.filter(Appointment.appointment_date <= to_date)

    appointments = query.all()

    return {
        "success": True,
        "data": [appointment.to_dict() for appointment in appointments]
    }
