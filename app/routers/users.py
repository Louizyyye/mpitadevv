"""
User routers for patient registration, login, and profile management
Handles CRUD operations for user accounts
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re
from app.database import get_db
from app.models import User, UserRole
from app.schemas.users import UserCreate, UserOut, UserUpdate
from app.utils.auth import create_access_token, create_refresh_token, get_current_user
from app.utils.security import hash_password, verify_password

router = APIRouter()

@router.get("/", response_model=list[dict])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [u.to_dict() for u in users]

@router.get("/{user_id}", response_model=dict)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()


# Pydantic schemas
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    national_id: str = Field(..., min_length=4, max_length=20)
    otp: str = Field(..., min_length=4, max_length=10)
    occupation: Optional[str] = Field(None, max_length=100)
    password: str = Field(..., min_length=8)

    @validator('phone')
    def validate_phone(cls, v):
        phone = re.sub(r'\s+', '', v)
        if not re.match(r'^\+?[0-9]{10,15}$', phone):
            raise ValueError('Invalid phone number format')
        return phone

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    occupation: Optional[str] = Field(None, max_length=100)

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            phone = re.sub(r'\s+', '', v)
            if not re.match(r'^\+?[0-9]{10,15}$', phone):
                raise ValueError('Invalid phone number format')
            return phone
        return v


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new patient"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if phone already exists
    existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )


    # Create new user (add national_id and otp fields if present in model)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        occupation=user_data.occupation,
        hashed_password=hash_password(user_data.password),
        role=UserRole.PATIENT,
        national_id=getattr(user_data, 'national_id', None),
        otp=getattr(user_data, 'otp', None)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate tokens
    access_token = create_access_token({"sub": str(new_user.id), "email": new_user.email})
    refresh_token = create_refresh_token({"sub": str(new_user.id)})

    return {
        "success": True,
        "message": "User registered successfully",
        "data": {
            "user": new_user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    }


@router.post("/login")
async def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT tokens"""
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )

    # Generate tokens
    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    }


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "success": True,
        "data": current_user.to_dict()
    }


@router.put("/profile")
async def update_profile(
        update_data: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Update current user profile"""
    # Check if phone is being changed and if it's already taken
    if update_data.phone and update_data.phone != current_user.phone:
        existing_phone = db.query(User).filter(
            User.phone == update_data.phone,
            User.id != current_user.id
        ).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use"
            )

    # Update fields
    if update_data.name:
        current_user.name = update_data.name
    if update_data.phone:
        current_user.phone = update_data.phone
    if update_data.occupation is not None:
        current_user.occupation = update_data.occupation

    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "message": "Profile updated successfully",
        "data": current_user.to_dict()
    }


@router.post("/change-password")
async def change_password(
        password_data: PasswordChange,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify old password
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Update password
    current_user.hashed_password = hash_password(password_data.new_password)
    db.commit()

    return {
        "success": True,
        "message": "Password changed successfully"
    }


@router.delete("/account")
async def delete_account(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Deactivate user account"""
    current_user.is_active = 0
    db.commit()

    return {
        "success": True,
        "message": "Account deactivated successfully"
    }