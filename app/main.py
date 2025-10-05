"""
Mpita Medical - FastAPI Backend
Main application entry point with CORS, exception handlers, and route registration.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, engine, get_db
from app.routers.users import router as users_router
from app.routers import appointments, payments
from app.utils.logger import setup_logger

# -------------------------------------------------------------------------
# Logger Setup
# -------------------------------------------------------------------------
logger = setup_logger()
logger.info("Initializing Mpita Medical API...")

# -------------------------------------------------------------------------
# Lifespan events (startup / shutdown)
# -------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context for startup and shutdown events."""
    # Startup
    logger.info("Starting Mpita Medical API backend...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {str(e)}", exc_info=True)
        raise

    yield  # ---- Application runs during this time ----

    # Shutdown
    logger.info("Shutting down Mpita Medical API backend...")

# -------------------------------------------------------------------------
# FastAPI Application Initialization
# -------------------------------------------------------------------------
app = FastAPI(
    title="Mpita Medical API",
    description="Backend API for Mpita Medical appointment and payment management.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

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
    """Handle FastAPI validation errors."""
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "errors": exc.errors()
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors."""
    logger.error(f"Database error on {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "A database error occurred. Please try again later."
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions globally."""
    logger.error(f"Unexpected error on {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred. Please try again later."
        }
    )

# -------------------------------------------------------------------------
# Health Check Endpoints
# -------------------------------------------------------------------------
@app.get("/", tags=["Health"])
async def root():
    """Simple root health check."""
    return {
        "success": True,
        "message": "Mpita Medical API is running",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check — verifies DB connection."""
    try:
        db_gen = get_db()
        db = next(db_gen)
        db.execute("SELECT 1")
        db.close()
        return {
            "success": True,
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
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
