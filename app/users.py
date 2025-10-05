from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User
from app.schemas.users import UserCreate, UserRead, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# -----------------------------------------------------
# CREATE USER
# -----------------------------------------------------
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password  # NOTE: in production, hash this before saving!
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# -----------------------------------------------------
# READ ALL USERS
# -----------------------------------------------------
@router.get("/", response_model=List[UserRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


# -----------------------------------------------------
# READ USER BY ID
# -----------------------------------------------------
@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# -----------------------------------------------------
# UPDATE USER
# -----------------------------------------------------
@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = user_update.name or user.name
    user.email = user_update.email or user.email
    user.password = user_update.password or user.password  # Again, hash before saving

    db.commit()
    db.refresh(user)
    return user


# -----------------------------------------------------
# DELETE USER
# -----------------------------------------------------
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return None
