from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.config import settings

# -----------------------------
# Password Hashing Configuration
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if plain password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# -----------------------------
# JWT Token Utilities
# -----------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with optional expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create a long-lived refresh token."""
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = {**data, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str, refresh: bool = False) -> dict:
    """Decode a JWT token and return its payload."""
    try:
        secret = settings.REFRESH_SECRET_KEY if refresh else settings.SECRET_KEY
        payload = jwt.decode(token, secret, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# -----------------------------
# Example Settings Reference
# -----------------------------
"""
Ensure you have these in your app/config.py:

class Settings:
    SECRET_KEY = "your_access_secret_key"
    REFRESH_SECRET_KEY = "your_refresh_secret_key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

settings = Settings()
"""

# -----------------------------
# Example Usage in your routers:
# -----------------------------
"""
from app.utils.security import hash_password, verify_password, create_access_token

# Registering a user
user.hashed_password = hash_password(password_input)

# Logging in
if not verify_password(password_input, user.hashed_password):
    raise HTTPException(status_code=400, detail="Incorrect password")

# Creating token
token = create_access_token({"sub": user.email})
"""
