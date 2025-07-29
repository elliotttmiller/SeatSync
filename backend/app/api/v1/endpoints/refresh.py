from fastapi import APIRouter, HTTPException, Depends, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import secrets
from pydantic import BaseModel
from app.models.database import User
from app.models.refresh_token import RefreshToken
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db

router = APIRouter()

REFRESH_TOKEN_EXPIRE_DAYS = 7

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(login_request: LoginRequest, db: AsyncSession = Depends(get_db), response: Response = None):
    print("DEBUG login_request:", login_request)
    email = login_request.email
    password = login_request.password
    # TODO: Implement async user authentication
    # user = await authenticate_user(email, password, db)
    # if not user:
    #     raise HTTPException(status_code=401, detail="Invalid credentials")
    # access_token = create_access_token(data={"sub": str(user.id)})
    # refresh_token_str = secrets.token_urlsafe(64)
    # expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    # refresh_token = RefreshToken(user_id=user.id, token=refresh_token_str, expires_at=expires_at)
    # db.add(refresh_token)
    # await db.commit()
    # await db.refresh(refresh_token)
    # if response:
    #     response.set_cookie(key="refresh_token", value=refresh_token_str, httponly=True, max_age=60*60*24*REFRESH_TOKEN_EXPIRE_DAYS)
    # return {"access_token": access_token, "token_type": "bearer"}
    return {"access_token": "dummy", "token_type": "bearer"}

@router.post("/refresh")
async def refresh_token(response: Response, db: AsyncSession = Depends(get_db)):
    # TODO: Implement async refresh logic
    return {"access_token": "dummy", "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response, db: AsyncSession = Depends(get_db)):
    # TODO: Implement async logout logic
    return {"message": "Logged out"}

@router.post("/debug")
async def debug_endpoint(request: Request):
    data = await request.json()
    print("DEBUG RAW BODY:", data)
    return data 