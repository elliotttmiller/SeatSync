import os
from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Developer mode bypass
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

class DevSuperUser:
    id = 1
    email = "dev@seatsync.com"
    full_name = "Developer Superuser"
    is_active = True
    is_verified = True
    subscription_tier = "admin"
    hashed_password = pwd_context.hash("devpassword")


def create_access_token(
    data: dict, expires_delta: Union[timedelta, None] = None
) -> str:
    """
    Create a JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    if DEV_MODE:
        return True
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)

def get_current_user_dev_bypass():
    if DEV_MODE:
        return DevSuperUser()
    return None

# HTTP Bearer security scheme
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get the current authenticated user from JWT token
    
    In DEV_MODE, returns a superuser without checking token
    """
    # Dev mode bypass
    if DEV_MODE:
        return DevSuperUser()
    
    # Extract token from credentials
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # In production, would query database for user
    # For now, return a mock user object with the ID
    class TokenUser:
        def __init__(self, user_id):
            self.id = int(user_id)
            self.email = f"user{user_id}@seatsync.com"
            self.is_active = True
            self.subscription_tier = "premium"
    
    return TokenUser(user_id) 