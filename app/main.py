"""
Mpita Medical - FastAPI Backend
Main application entry point with CORS, exception handlers, and route registration.
Includes dedicated Daraja endpoints for STK Push, Airtime, and Bank payments.
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
from pathlib import Path

from app.database import Base, engine, get_db
from app.routers.users import router as users_router
from app.routers import appointments, payments
from app.utils.logger import setup_logger
from app.daraja_client import stk_push, airtime_push, bank_payment  # Assuming you have these functions

# -------------------------------------------------------------------------
if os.getenv("DAR_AJA_ENV") is None:
    BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

# -------------------------------------------------------------------------
# Logger Setup
# -------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mpita.backend")

# -------------------------------------------------------------------------
# Environment Variables

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("❌ SECRET_KEY not found. Please set it in environment variables.")
logger.info(f"SECRET_KEY loaded successfully: {SECRET_KEY[:10]}****")

# -------------------------------------------------------------------------
# Lifespan events (startup / shutdown)
# -------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Starting Mpita Medical API backend...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {str(e)}", exc_info=True)
        raise

    yield

    logger.info("Shutting down Mpita Medical API backend...")

# -------------------------------------------------------------------------
# FastAPI Application Initialization
# -------------------------------------------------------------------------
app = FastAPI(
    title="Mpita Medical API",
    description="Backend API for appointments, payments, and donations.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)


class OTPRequest(BaseModel):
  phone: str


class PatientRegister(BaseModel):
  full_name: str
  username: str
  national_id: str
  phone: str
  email: str
  password: str
  otp: str
  payment: str

class Patient(BaseModel):
    full_name: str
    username: str
    national_id: str
    phone: str
    email: str
    password: str
    otp: str
    payment: str


class PatientLogin(BaseModel):
    email: str
    password: str


@app.post("/send-otp")
async def send_otp(data: OTPRequest):
  # Generate OTP and send SMS
  return {"message": "OTP sent"}


@app.post("/register-patient")
async def register_patient(data: PatientRegister):
  # Verify OTP
  # Save patient data to DB
  # Return success or failure
  return {"message": "Patient registered", "username": data.username}

@app.post("/register-patient")
async def register_patient(patient: Patient):
    # Here, save patient to DB, verify OTP, etc.
    # Example response:
    return {"username": patient.username, "status": "registered"}

@app.post("/patient-login")
async def patient_login(login: PatientLogin):
    # Verify credentials
    if login.email == "test@example.com" and login.password == "secret":
        return {"username": "John Doe"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
# -------------------------------------------------------------------------
# Daraja Models
# -------------------------------------------------------------------------
class STKRequest(BaseModel):
    phone_number: str = Field(..., example="254712345678")
    amount: float = Field(..., gt=0)
    account_reference: Optional[str] = Field("MpitaTest", example="INV123")
    description: Optional[str] = Field("Payment", example="Lipa na M-Pesa")

class AirtimeRequest(BaseModel):
    phone_number: str = Field(..., example="254712345678")
    amount: float = Field(..., gt=0)
    provider: Optional[str] = Field("Safaricom", example="Safaricom")

class BankPaymentRequest(BaseModel):
    account_number: str = Field(..., example="1234567890")
    bank_code: str = Field(..., example="01")
    amount: float = Field(..., gt=0)
    reference: Optional[str] = Field("MpitaBank", example="PAY123")

# -------------------------------------------------------------------------
# Daraja API Endpoints
# -------------------------------------------------------------------------
@app.post("/mpesa/stk", tags=["Daraja"])
async def start_stk(req: STKRequest):
    """Trigger an STK push for payments, donations, or booking."""
    try:
        result = await stk_push(
            phone_number=req.phone_number,
            amount=req.amount,
            account_reference=req.account_reference,
            description=req.description
        )
        return {"success": True, "daraja": result}
    except Exception as exc:
        logger.exception("Failed to call STK Push")
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/mpesa/airtime", tags=["Daraja"])
async def send_airtime(req: AirtimeRequest):
    """Send Airtime to user."""
    try:
        result = await airtime_push(
            phone_number=req.phone_number,
            amount=req.amount,
            provider=req.provider
        )
        return {"success": True, "airtime": result}
    except Exception as exc:
        logger.exception("Failed to send Airtime")
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/mpesa/bank", tags=["Daraja"])
async def send_bank_payment(req: BankPaymentRequest):
    """Send bank payment to user."""
    try:
        result = await bank_payment(
            account_number=req.account_number,
            bank_code=req.bank_code,
            amount=req.amount,
            reference=req.reference
        )
        return {"success": True, "bank_payment": result}
    except Exception as exc:
        logger.exception("Failed to send Bank Payment")
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/mpesa/callback", tags=["Daraja"])
async def mpesa_callback(payload: dict):
    """Receive Daraja payment callbacks (STK, donations, bookings)."""
    logger.info("Received M-Pesa callback: %s", payload)
    return {"status": "received"}

# -------------------------------------------------------------------------
# CORS Configuration
# -------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://mpitamedical.com",
        "https://*.mpitamedical.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------------
# Exception Handlers
# -------------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "message": "Validation error", "errors": exc.errors()}
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error on {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "A database error occurred. Please try again later."}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error on {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "An unexpected error occurred. Please try again later."}
    )

# -------------------------------------------------------------------------
# Health Check Endpoints
# -------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    try:
        db_gen = get_db()
        db = next(db_gen)
        db.execute("SELECT 1")
        db.close()
        return {"success": True, "status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"success": False, "status": "unhealthy", "database": "disconnected", "error": str(e)}
        )

# -------------------------------------------------------------------------
# Routers Registration
# -------------------------------------------------------------------------
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])

# -------------------------------------------------------------------------
# Run (for local dev)
# -------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

