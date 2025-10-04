"""
Mpita Medical - FastAPI Backend
Main application entry point with CORS, exception handlers, and route registration
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging
from contextlib import asynccontextmanager

from contextlib import contextmanager
from app.database import get_db, Base, engine
from app.models import User
from app.routers import  appointments, payments
from app.routers.users import router as users_router
from app.utils.logger import setup_logger
from fastapi import FastAPI

app = FastAPI()
from app.database import SessionLocal
db = SessionLocal()

users = db.query(User).all()



app.include_router(users_router, prefix="/api/users", tags=["Users"])
# Initialize database (create tables) if needed
def init_database():
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db_context():
    db_gen = get_db()
    db = next(db_gen)
    try:
        yield db
    finally:
        db_gen.close()

# Usage:
with get_db_context() as db:
    # This is the indented block
    users = db.query(User).all()
    for user in users:
        print(user.to_dict())


# Setup logger
logger = setup_logger()
logger.info("Application started successfully")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    logger.info("Starting Mpita Medical API...")
    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Mpita Medical API...")


# Initialize FastAPI app
app = FastAPI(
    title="Mpita Medical API",
    description="Backend API for Mpita Medical appointment and payment management",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS Configuration
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


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
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
    """Handle database errors"""
    logger.error(f"Database error on {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Database error occurred. Please try again later."
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unexpected error on {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "success": True,
        "message": "Mpita Medical API is running",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    try:
        # Test database connection
        from app.database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()

        return {
            "success": True,
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


# Register routers
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )