"""
AI Service for SeatSync Phase 2 - AI Intelligence Layer

This service provides comprehensive AI-powered capabilities including:
- Advanced price prediction with context analysis
- Intelligent portfolio recommendations  
- Market sentiment analysis
- Automated insights generation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import re

# Use existing google-genai package instead of google-generativeai
import google.genai as genai
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, text
from google.cloud import bigquery
from google.oauth2 import service_account

from app.core.config import settings
from app.models.database import (
    User, SeasonTicket, Listing, AIPrediction, 
    MarketplaceAccount, AutomationRule
)

logger = logging.getLogger(__name__)

class AIService:
    """Comprehensive AI service for SeatSync Phase 2 capabilities"""
    
    def __init__(self):
        # Configure Gemini AI using the existing google-genai package
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        except Exception as e:
            logger.warning(f"Could not configure Gemini AI: {e}")
            self.client = None
        
    async def predict_ticket_price(
        self, 
        ticket_data: Dict[str, Any], 
        db: AsyncSession,
        include_context: bool = True
    ) -> Dict[str, Any]:
        """
        AI-powered price prediction with comprehensive market analysis
        
        Args:
            ticket_data: Ticket information including venue, team, date, section, etc.
            db: Database session for historical data lookup
            include_context: Whether to include market context in prediction
            
        Returns:
            Prediction result with price, confidence, reasoning, and recommendations
        """
        try:
            logger.info(f"Predicting price for ticket: {ticket_data.get('game_id', 'unknown')}")
            
            # 1. Extract ticket details
            team = ticket_data.get("team", "")
            opponent = ticket_data.get("opponent", "")
            date = ticket_data.get("game_date", "")
            section = ticket_data.get("section", "")
            row = ticket_data.get("row", "")
            seat_count = ticket_data.get("seat_count", 1)
            venue = ticket_data.get("venue", "")
            
            # 2. Gather historical context
            historical_context = ""
            market_trends = {}
            
            if include_context:
                historical_context = await self._get_historical_pricing_context(
                    db, team, venue, section
                )
                market_trends = await self._analyze_market_trends(db, team)
            
            # 3. Build comprehensive AI prompt
            prompt = self._build_pricing_prompt(
                ticket_data, historical_context, market_trends
            )
            
            # 4. Generate AI prediction
            response = await self._generate_ai_response(prompt)
            
            # 5. Parse structured response
            prediction_result = await self._parse_pricing_response(response)
            
            # 6. Store prediction in database
            await self._store_prediction(db, ticket_data, prediction_result)
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"Price prediction error: {e}")
            return {
                "predicted_price": 0,
                "confidence": 0,
                "reasoning": f"Error in prediction: {str(e)}",
                "recommendations": []
            }
    
    async def generate_portfolio_insights(
        self, 
        user_id: str, 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Generate AI-driven portfolio insights and recommendations
        
        Args:
            user_id: User identifier
            db: Database session
            
        Returns:
            Portfolio analysis with insights, recommendations, and alerts
        """
        try:
            logger.info(f"Generating portfolio insights for user: {user_id}")
            
            # 1. Gather user portfolio data
            portfolio_data = await self._get_user_portfolio_data(db, user_id)
            
            # 2. Analyze performance metrics
            performance_analysis = await self._analyze_portfolio_performance(
                portfolio_data
            )
            
            # 3. Generate AI insights
            insights_prompt = self._build_portfolio_insights_prompt(
                portfolio_data, performance_analysis
            )
            
            response = await self._generate_ai_response(insights_prompt)
            insights = await self._parse_portfolio_insights(response)
            
            return {
                "summary": performance_analysis,
                "ai_insights": insights,
                "recommendations": insights.get("recommendations", []),
                "alerts": insights.get("alerts", []),
                "optimization_suggestions": insights.get("optimizations", [])
            }
            
        except Exception as e:
            logger.error(f"Portfolio insights error: {e}")
            return {
                "summary": {},
                "ai_insights": {"error": str(e)},
                "recommendations": [],
                "alerts": [],
                "optimization_suggestions": []
            }
    
    async def analyze_market_sentiment(
        self, 
        team: str, 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Analyze market sentiment for a specific team using AI
        
        Args:
            team: Team name to analyze
            db: Database session
            
        Returns:
            Sentiment analysis with trends and predictions
        """
        try:
            # 1. Gather recent market data
            market_data = await self._get_team_market_data(db, team)
            
            # 2. Build sentiment analysis prompt
            sentiment_prompt = f"""
            Analyze the market sentiment for {team} based on the following data:
            
            Recent listing data: {market_data.get('recent_listings', [])}
            Price trends: {market_data.get('price_trends', {})}
            Sales volume: {market_data.get('volume_trends', {})}
            
            Provide analysis in JSON format:
            {{
                "sentiment_score": 0-100,
                "sentiment_label": "bullish/bearish/neutral",
                "key_factors": ["factor1", "factor2"],
                "price_prediction": "increase/decrease/stable",
                "confidence": 0-100,
                "reasoning": "detailed explanation"
            }}
            """
            
            response = await self._generate_ai_response(sentiment_prompt)
            sentiment_analysis = json.loads(response.strip())
            
            return sentiment_analysis
            
        except Exception as e:
            logger.error(f"Market sentiment analysis error: {e}")
            return {
                "sentiment_score": 50,
                "sentiment_label": "neutral", 
                "key_factors": ["Error in analysis"],
                "price_prediction": "stable",
                "confidence": 0,
                "reasoning": f"Analysis failed: {str(e)}"
            }
    
    async def generate_smart_pricing_recommendation(
        self,
        listing_data: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Generate AI-powered pricing recommendations for ticket listings
        
        Args:
            listing_data: Current listing information
            db: Database session
            
        Returns:
            Pricing recommendations with optimal prices and strategies
        """
        try:
            # 1. Get competitive analysis
            competitive_data = await self._get_competitive_pricing_data(
                db, listing_data
            )
            
            # 2. Build pricing recommendation prompt
            pricing_prompt = f"""
            As a ticket pricing expert, analyze this listing and provide pricing recommendations:
            
            Listing Details:
            {json.dumps(listing_data, indent=2)}
            
            Competitive Analysis:
            {json.dumps(competitive_data, indent=2)}
            
            Provide recommendations in JSON format:
            {{
                "optimal_price": 150.00,
                "price_range": {{"min": 140.00, "max": 165.00}},
                "strategy": "aggressive/moderate/conservative",
                "reasoning": "detailed explanation",
                "time_sensitivity": "high/medium/low",
                "expected_sale_probability": 0-100,
                "recommendations": ["action1", "action2"]
            }}
            """
            
            response = await self._generate_ai_response(pricing_prompt)
            pricing_rec = json.loads(response.strip())
            
            return pricing_rec
            
        except Exception as e:
            logger.error(f"Smart pricing recommendation error: {e}")
            return {
                "optimal_price": 0,
                "price_range": {"min": 0, "max": 0},
                "strategy": "conservative",
                "reasoning": f"Error: {str(e)}",
                "time_sensitivity": "low",
                "expected_sale_probability": 0,
                "recommendations": []
            }
    
    # Private helper methods
    
    async def _get_historical_pricing_context(
        self, 
        db: AsyncSession, 
        team: str, 
        venue: str, 
        section: str
    ) -> str:
        """Get historical pricing context for similar tickets"""
        try:
            # Query similar historical listings
            query = text("""
                SELECT AVG(l.price) as avg_price, COUNT(*) as count,
                       MIN(l.price) as min_price, MAX(l.price) as max_price
                FROM listings l
                JOIN season_tickets st ON l.season_ticket_id = st.id
                WHERE st.team_name LIKE :team 
                  AND st.venue LIKE :venue
                  AND l.section LIKE :section
                  AND l.status = 'sold'
                  AND l.listed_date >= date('now', '-90 days')
            """)
            
            result = await db.execute(
                query, 
                {"team": f"%{team}%", "venue": f"%{venue}%", "section": f"%{section}%"}
            )
            row = result.fetchone()
            
            if row and row[1] > 0:  # count > 0
                return f"Historical data: {row[1]} similar tickets sold, avg ${row[0]:.2f}, range ${row[2]:.2f}-${row[3]:.2f}"
            else:
                return "Limited historical data available for similar tickets"
                
        except Exception as e:
            logger.error(f"Error getting historical context: {e}")
            return "Historical data unavailable"
    
    async def _analyze_market_trends(self, db: AsyncSession, team: str) -> Dict[str, Any]:
        """Analyze market trends for the team"""
        try:
            # Get recent trends
            query = text("""
                SELECT 
                    DATE(l.listed_date) as date,
                    AVG(l.price) as avg_price,
                    COUNT(*) as volume
                FROM listings l
                JOIN season_tickets st ON l.season_ticket_id = st.id
                WHERE st.team_name LIKE :team
                  AND l.listed_date >= date('now', '-30 days')
                GROUP BY DATE(l.listed_date)
                ORDER BY date DESC
                LIMIT 30
            """)
            
            result = await db.execute(query, {"team": f"%{team}%"})
            rows = result.fetchall()
            
            if rows:
                prices = [float(row[1]) for row in rows]
                volumes = [int(row[2]) for row in rows]
                
                return {
                    "avg_price_trend": sum(prices) / len(prices),
                    "avg_volume_trend": sum(volumes) / len(volumes),
                    "price_volatility": max(prices) - min(prices) if len(prices) > 1 else 0,
                    "data_points": len(rows)
                }
            else:
                return {"avg_price_trend": 0, "avg_volume_trend": 0, "price_volatility": 0}
                
        except Exception as e:
            logger.error(f"Error analyzing market trends: {e}")
            return {}
    
    def _build_pricing_prompt(
        self, 
        ticket_data: Dict[str, Any], 
        historical_context: str, 
        market_trends: Dict[str, Any]
    ) -> str:
        """Build comprehensive AI prompt for price prediction"""
        return f"""
You are an expert ticket pricing analyst. Analyze the following ticket and provide a pricing recommendation:

TICKET DETAILS:
{json.dumps(ticket_data, indent=2)}

HISTORICAL CONTEXT:
{historical_context}

MARKET TRENDS:
{json.dumps(market_trends, indent=2)}

Please provide your analysis in the following JSON format:
{{
    "predicted_price": 150.00,
    "confidence": 85,
    "price_range": {{"min": 140.00, "max": 165.00}},
    "reasoning": "Detailed explanation of pricing factors",
    "key_factors": ["factor1", "factor2", "factor3"],
    "market_comparison": "compared to similar listings",
    "recommendations": ["recommendation1", "recommendation2"]
}}

Consider factors like:
- Team performance and popularity
- Game importance (playoffs, rivalries, etc.)
- Seat location quality
- Historical pricing patterns
- Market supply and demand
- Time until game date
- Day of week and time
"""

    async def _generate_ai_response(self, prompt: str) -> str:
        """Generate AI response using Gemini via HTTP API"""
        try:
            if not settings.GEMINI_API_KEY:
                return '{"response": "AI service not configured"}'
            
            # Use HTTP client to call Gemini API directly
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={settings.GEMINI_API_KEY}",
                    json={
                        "contents": [{
                            "parts": [{
                                "text": prompt
                            }]
                        }]
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    logger.error(f"Gemini API error: {response.status_code}")
                    return '{"response": "AI service temporarily unavailable"}'
                    
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return '{"response": "AI response generation failed"}'
    
    async def _parse_pricing_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate AI pricing response"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                # Validate required fields
                if "predicted_price" not in result:
                    result["predicted_price"] = 0
                if "confidence" not in result:
                    result["confidence"] = 50
                    
                return result
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.error(f"Error parsing pricing response: {e}")
            return {
                "predicted_price": 0,
                "confidence": 0,
                "reasoning": f"Parse error: {str(e)}",
                "recommendations": []
            }
    
    async def _store_prediction(
        self, 
        db: AsyncSession, 
        ticket_data: Dict[str, Any], 
        prediction: Dict[str, Any]
    ) -> None:
        """Store AI prediction in database"""
        try:
            # Create prediction record (assuming AIPrediction model exists)
            # This would be implemented based on your actual model structure
            pass
        except Exception as e:
            logger.error(f"Error storing prediction: {e}")
    
    async def _get_user_portfolio_data(self, db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Gather comprehensive user portfolio data"""
        # Implementation would fetch user's tickets, listings, performance metrics, etc.
        return {}
    
    async def _analyze_portfolio_performance(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze portfolio performance metrics"""
        return {}
    
    def _build_portfolio_insights_prompt(self, portfolio_data: Dict, performance: Dict) -> str:
        """Build portfolio insights prompt"""
        return f"""
        Analyze this ticket portfolio and provide insights:
        Portfolio: {portfolio_data}
        Performance: {performance}
        Provide insights in JSON format with recommendations, alerts, and optimization suggestions.
        """
    
    async def _parse_portfolio_insights(self, response: str) -> Dict[str, Any]:
        """Parse portfolio insights from AI response"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except:
            return {}
    
    async def _get_team_market_data(self, db: AsyncSession, team: str) -> Dict[str, Any]:
        """Get market data for team sentiment analysis"""
        return {}
    
    async def _get_competitive_pricing_data(
        self, 
        db: AsyncSession, 
        listing_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get competitive pricing data for recommendations"""
        return {}