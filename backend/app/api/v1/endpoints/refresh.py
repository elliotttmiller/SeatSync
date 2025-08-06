from fastapi import APIRouter, HTTPException, Depends, status, Response, Request, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import secrets
import logging
from pydantic import BaseModel
from app.models.database import User
from app.models.refresh_token import RefreshToken
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.db.session import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

REFRESH_TOKEN_EXPIRE_DAYS = 7

class LoginRequest(BaseModel):
    email: str
    password: str

async def authenticate_user(email: str, password: str, db: AsyncSession):
    """Authenticate user with email and password"""
    try:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    except Exception as e:
        logger.error(f"Error authenticating user {email}: {e}")
        return None

@router.post("/login")
async def login(login_request: LoginRequest, db: AsyncSession = Depends(get_db), response: Response = None):
    """Authenticate user and return access token"""
    logger.info(f"Login attempt for email: {login_request.email}")
    
    try:
        user = await authenticate_user(login_request.email, login_request.password, db)
        if not user:
            logger.warning(f"Failed login attempt for email: {login_request.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Create refresh token
        refresh_token_str = secrets.token_urlsafe(64)
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        refresh_token = RefreshToken(
            user_id=user.id, 
            token=refresh_token_str, 
            expires_at=expires_at
        )
        
        db.add(refresh_token)
        await db.commit()
        await db.refresh(refresh_token)
        
        # Set httponly cookie for refresh token
        if response:
            response.set_cookie(
                key="refresh_token", 
                value=refresh_token_str, 
                httponly=True, 
                max_age=60*60*24*REFRESH_TOKEN_EXPIRE_DAYS,
                secure=settings.NODE_ENV == "production",
                samesite="lax"
            )
        
        logger.info(f"Successful login for user: {user.email}")
        return {"access_token": access_token, "token_type": "bearer", "user_id": str(user.id)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {login_request.email}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during login")

@router.post("/refresh")
async def refresh_token(response: Response, db: AsyncSession = Depends(get_db), refresh_token: str = Cookie(None)):
    """Refresh access token using refresh token"""
    logger.info("Token refresh attempt")
    
    try:
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token not provided")
        
        # Find refresh token in database
        result = await db.execute(
            select(RefreshToken)
            .where(RefreshToken.token == refresh_token)
            .where(RefreshToken.expires_at > datetime.utcnow())
        )
        token_record = result.scalar_one_or_none()
        
        if not token_record:
            logger.warning("Invalid or expired refresh token")
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        
        # Get user
        user_result = await db.execute(select(User).where(User.id == token_record.user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            logger.error(f"User not found for refresh token: {token_record.user_id}")
            raise HTTPException(status_code=401, detail="User not found")
        
        # Create new access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Optional: Create new refresh token for better security
        new_refresh_token_str = secrets.token_urlsafe(64)
        new_expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        # Update the refresh token
        token_record.token = new_refresh_token_str
        token_record.expires_at = new_expires_at
        
        await db.commit()
        
        # Update cookie
        if response:
            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token_str,
                httponly=True,
                max_age=60*60*24*REFRESH_TOKEN_EXPIRE_DAYS,
                secure=settings.NODE_ENV == "production",
                samesite="lax"
            )
        
        logger.info(f"Token refreshed successfully for user: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during token refresh")

@router.post("/logout")
async def logout(response: Response, db: AsyncSession = Depends(get_db), refresh_token: str = Cookie(None)):
    """Logout user and invalidate refresh token"""
    logger.info("Logout attempt")
    
    try:
        if refresh_token:
            # Remove refresh token from database
            result = await db.execute(
                select(RefreshToken).where(RefreshToken.token == refresh_token)
            )
            token_record = result.scalar_one_or_none()
            
            if token_record:
                await db.delete(token_record)
                await db.commit()
                logger.info("Refresh token deleted from database")
        
        # Clear cookie
        if response:
            response.delete_cookie(key="refresh_token")
        
        logger.info("User logged out successfully")
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during logout")

@router.post("/debug")
async def debug_endpoint(request: Request):
    """Debug endpoint for development"""
    data = await request.json()
    logger.debug(f"DEBUG RAW BODY: {data}")
    return data 