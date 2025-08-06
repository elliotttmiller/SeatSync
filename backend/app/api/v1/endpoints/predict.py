from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import get_db
from app.services.ai_service import AIService
from pydantic import BaseModel
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize AI service
ai_service = AIService()

class PredictionRequest(BaseModel):
    team: str
    opponent: Optional[str] = ""
    game_date: str
    venue: str
    section: str
    row: Optional[str] = ""
    seat_count: int = 1
    game_id: Optional[str] = ""
    additional_context: Optional[Dict[str, Any]] = {}

class SmartPricingRequest(BaseModel):
    listing_id: Optional[str] = ""
    team: str
    game_date: str
    section: str
    current_price: float
    days_until_game: int
    similar_listings_count: int = 0

@router.post("/predict-price")
async def predict_price(
    request: PredictionRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    AI-powered ticket price prediction with comprehensive market analysis
    
    This endpoint uses advanced AI to analyze ticket data, historical patterns,
    and market trends to provide accurate price predictions with confidence scores.
    """
    try:
        logger.info(f"Processing price prediction for {request.team} vs {request.opponent}")
        
        # Convert request to dict for AI service
        ticket_data = request.dict()
        
        # Get AI prediction
        prediction_result = await ai_service.predict_ticket_price(
            ticket_data=ticket_data,
            db=db,
            include_context=True
        )
        
        return {
            "status": "success",
            "prediction": prediction_result,
            "metadata": {
                "team": request.team,
                "game_date": request.game_date,
                "processing_time": "completed"
            }
        }
        
    except Exception as e:
        logger.error(f"Price prediction error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Price prediction failed: {str(e)}"
        )

@router.post("/smart-pricing-recommendation")
async def smart_pricing_recommendation(
    request: SmartPricingRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI-powered smart pricing recommendations for ticket listings
    
    Provides optimal pricing strategies based on market conditions,
    competitive analysis, and time-sensitive factors.
    """
    try:
        logger.info(f"Generating smart pricing for {request.team} listing")
        
        # Convert request to listing data format
        listing_data = request.dict()
        
        # Get pricing recommendation
        pricing_rec = await ai_service.generate_smart_pricing_recommendation(
            listing_data=listing_data,
            db=db
        )
        
        return {
            "status": "success",
            "pricing_recommendation": pricing_rec,
            "current_price": request.current_price,
            "team": request.team
        }
        
    except Exception as e:
        logger.error(f"Smart pricing error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Smart pricing recommendation failed: {str(e)}"
        )

@router.get("/market-sentiment/{team}")
async def get_market_sentiment(
    team: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze market sentiment for a specific team using AI
    
    Provides sentiment analysis, price predictions, and key market factors
    affecting ticket prices for the specified team.
    """
    try:
        logger.info(f"Analyzing market sentiment for {team}")
        
        sentiment_analysis = await ai_service.analyze_market_sentiment(
            team=team,
            db=db
        )
        
        return {
            "status": "success",
            "team": team,
            "sentiment_analysis": sentiment_analysis
        }
        
    except Exception as e:
        logger.error(f"Market sentiment analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Market sentiment analysis failed: {str(e)}"
        ) 