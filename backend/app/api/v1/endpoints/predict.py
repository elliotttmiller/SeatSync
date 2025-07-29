from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import get_db
import requests
import os

router = APIRouter()

@router.post("/predict-price")
async def predict_price(ticket: dict, db: AsyncSession = Depends(get_db)):
    # TODO: Implement async BigQuery and Gemini logic
    return {"reasoning": "dummy", "price": "...parse price from result..."} 