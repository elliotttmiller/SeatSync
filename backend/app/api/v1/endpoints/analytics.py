from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, text
from datetime import datetime, timedelta
import logging

from app.db.session import get_db
from app.models.database import (
    User, SeasonTicket, Listing, AIPrediction, 
    MarketplaceAccount, AutomationRule
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/portfolio-summary")
async def get_portfolio_summary(
    user_id: str = None,  # In production, this would come from JWT token
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get portfolio summary analytics for a user.
    """
    try:
        logger.info(f"Getting portfolio summary for user: {user_id}")
        
        # For development, get data for any user if user_id not provided
        if not user_id:
            # Get first user for demo purposes
            user_result = await db.execute(select(User).limit(1))
            user = user_result.scalar_one_or_none()
            if user:
                user_id = str(user.id)
            else:
                logger.warning("No users found in database")
                return {
                    "total_tickets": 0,
                    "total_value": 0.0,
                    "active_listings": 0,
                    "monthly_revenue": 0.0,
                    "total_cost_basis": 0.0,
                    "unrealized_pnl": 0.0,
                    "realized_pnl": 0.0
                }

        # Get total season tickets for user
        tickets_result = await db.execute(
            select(func.count(SeasonTicket.id))
            .where(SeasonTicket.user_id == user_id)
        )
        total_tickets = tickets_result.scalar() or 0

        # Get total cost basis
        cost_basis_result = await db.execute(
            select(func.sum(SeasonTicket.cost_basis))
            .where(SeasonTicket.user_id == user_id)
        )
        total_cost_basis = float(cost_basis_result.scalar() or 0)

        # Get active listings count
        active_listings_result = await db.execute(
            select(func.count(Listing.id))
            .join(SeasonTicket, Listing.season_ticket_id == SeasonTicket.id)
            .where(
                and_(
                    SeasonTicket.user_id == user_id,
                    Listing.status == 'active'
                )
            )
        )
        active_listings = active_listings_result.scalar() or 0

        # Get total value of active listings
        active_value_result = await db.execute(
            select(func.sum(Listing.price))
            .join(SeasonTicket, Listing.season_ticket_id == SeasonTicket.id)
            .where(
                and_(
                    SeasonTicket.user_id == user_id,
                    Listing.status == 'active'
                )
            )
        )
        total_value = float(active_value_result.scalar() or 0)

        # Get monthly revenue (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        monthly_revenue_result = await db.execute(
            select(func.sum(Listing.final_price))
            .join(SeasonTicket, Listing.season_ticket_id == SeasonTicket.id)
            .where(
                and_(
                    SeasonTicket.user_id == user_id,
                    Listing.status == 'sold',
                    Listing.sold_at >= thirty_days_ago
                )
            )
        )
        monthly_revenue = float(monthly_revenue_result.scalar() or 0)

        # Calculate realized P&L (sold tickets)
        realized_pnl_result = await db.execute(
            select(
                func.sum(Listing.final_price).label('total_sold'),
                func.count(Listing.id).label('tickets_sold')
            )
            .join(SeasonTicket, Listing.season_ticket_id == SeasonTicket.id)
            .where(
                and_(
                    SeasonTicket.user_id == user_id,
                    Listing.status == 'sold'
                )
            )
        )
        realized_result = realized_pnl_result.first()
        total_sold = float(realized_result.total_sold or 0) if realized_result else 0
        tickets_sold = realized_result.tickets_sold or 0 if realized_result else 0

        # Estimate cost per ticket for P&L calculation
        cost_per_ticket = total_cost_basis / total_tickets if total_tickets > 0 else 0
        realized_pnl = total_sold - (tickets_sold * cost_per_ticket)

        # Calculate unrealized P&L (current listing value vs cost)
        remaining_tickets = total_tickets - tickets_sold
        unrealized_pnl = total_value - (remaining_tickets * cost_per_ticket)

        result = {
            "total_tickets": total_tickets,
            "total_value": total_value,
            "active_listings": active_listings,
            "monthly_revenue": monthly_revenue,
            "total_cost_basis": total_cost_basis,
            "unrealized_pnl": unrealized_pnl,
            "realized_pnl": realized_pnl,
            "tickets_sold": tickets_sold
        }
        
        logger.info(f"Portfolio summary calculated: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating portfolio summary: {e}")
        raise HTTPException(status_code=500, detail="Error calculating portfolio summary")

@router.get("/market-trends")
async def get_market_trends(
    user_id: str = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get market trends analytics.
    """
    try:
        logger.info("Getting market trends")
        
        # Get recent price trends from listings
        recent_listings_result = await db.execute(
            select(
                Listing.game_date,
                func.avg(Listing.price).label('avg_price'),
                func.count(Listing.id).label('listing_count')
            )
            .where(
                and_(
                    Listing.created_at >= datetime.utcnow() - timedelta(days=30),
                    Listing.status.in_(['active', 'sold'])
                )
            )
            .group_by(Listing.game_date)
            .order_by(desc(Listing.game_date))
            .limit(10)
        )
        
        price_trends = []
        for row in recent_listings_result:
            price_trends.append({
                "date": row.game_date.isoformat(),
                "avg_price": float(row.avg_price or 0),
                "listing_count": row.listing_count
            })

        # Get AI prediction insights if available
        recent_predictions_result = await db.execute(
            select(
                AIPrediction.model_type,
                func.avg(AIPrediction.predicted_value).label('avg_prediction'),
                func.avg(AIPrediction.confidence_score).label('avg_confidence')
            )
            .where(AIPrediction.created_at >= datetime.utcnow() - timedelta(days=7))
            .group_by(AIPrediction.model_type)
        )
        
        demand_forecast = {}
        for row in recent_predictions_result:
            demand_forecast[row.model_type] = {
                "avg_prediction": float(row.avg_prediction or 0),
                "avg_confidence": float(row.avg_confidence or 0)
            }

        # Simple market sentiment based on recent listing activity
        sentiment_result = await db.execute(
            select(func.count(Listing.id).label('recent_listings'))
            .where(Listing.created_at >= datetime.utcnow() - timedelta(days=7))
        )
        recent_listings_count = sentiment_result.scalar() or 0
        
        # Determine sentiment based on listing activity
        if recent_listings_count > 50:
            market_sentiment = "bullish"
        elif recent_listings_count > 20:
            market_sentiment = "neutral"
        else:
            market_sentiment = "bearish"

        result = {
            "price_trends": price_trends,
            "demand_forecast": demand_forecast,
            "market_sentiment": market_sentiment,
            "recent_activity": recent_listings_count
        }
        
        logger.info(f"Market trends calculated: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating market trends: {e}")
        raise HTTPException(status_code=500, detail="Error calculating market trends")

@router.get("/user-performance")  
async def get_user_performance(
    user_id: str = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get user performance metrics.
    """
    try:
        logger.info(f"Getting user performance for user: {user_id}")
        
        if not user_id:
            # Get first user for demo purposes
            user_result = await db.execute(select(User).limit(1))
            user = user_result.scalar_one_or_none()
            if user:
                user_id = str(user.id)
            else:
                return {
                    "total_roi": 0.0,
                    "best_performing_team": None,
                    "worst_performing_team": None,
                    "avg_sale_time": 0,
                    "success_rate": 0.0
                }

        # Calculate ROI by team
        team_performance_result = await db.execute(
            text("""
                SELECT 
                    st.team,
                    COUNT(l.id) as total_listings,
                    SUM(CASE WHEN l.status = 'sold' THEN 1 ELSE 0 END) as sold_count,
                    AVG(CASE WHEN l.status = 'sold' THEN l.final_price ELSE NULL END) as avg_sale_price,
                    AVG(st.cost_basis / NULLIF(st.total_games, 0)) as avg_cost_per_ticket
                FROM season_tickets st
                LEFT JOIN listings l ON st.id = l.season_ticket_id
                WHERE st.user_id = :user_id
                GROUP BY st.team, st.cost_basis, st.total_games
                HAVING COUNT(l.id) > 0
            """), {"user_id": user_id}
        )
        
        team_metrics = []
        best_roi = -float('inf')
        worst_roi = float('inf')
        best_team = None
        worst_team = None
        
        for row in team_performance_result:
            avg_sale_price = float(row.avg_sale_price or 0)
            avg_cost = float(row.avg_cost_per_ticket or 0)
            
            if avg_cost > 0:
                roi = (avg_sale_price - avg_cost) / avg_cost * 100
            else:
                roi = 0
            
            team_metric = {
                "team": row.team,
                "roi": roi,
                "total_listings": row.total_listings,
                "sold_count": row.sold_count,
                "success_rate": (row.sold_count / row.total_listings * 100) if row.total_listings > 0 else 0
            }
            team_metrics.append(team_metric)
            
            if roi > best_roi:
                best_roi = roi
                best_team = row.team
            if roi < worst_roi:
                worst_roi = roi  
                worst_team = row.team

        # Calculate average sale time
        avg_sale_time_result = await db.execute(
            select(
                func.avg(
                    func.extract('epoch', Listing.sold_at - Listing.created_at) / 86400
                ).label('avg_days')
            )
            .join(SeasonTicket, Listing.season_ticket_id == SeasonTicket.id)
            .where(
                and_(
                    SeasonTicket.user_id == user_id,
                    Listing.status == 'sold',
                    Listing.sold_at.isnot(None)
                )
            )
        )
        avg_sale_time = float(avg_sale_time_result.scalar() or 0)

        # Overall success rate
        overall_success_result = await db.execute(
            select(
                func.count(Listing.id).label('total'),
                func.sum(
                    func.case((Listing.status == 'sold', 1), else_=0)
                ).label('sold')
            )
            .join(SeasonTicket, Listing.season_ticket_id == SeasonTicket.id)
            .where(SeasonTicket.user_id == user_id)
        )
        success_stats = overall_success_result.first()
        total_listings = success_stats.total or 0
        sold_listings = success_stats.sold or 0
        overall_success_rate = (sold_listings / total_listings * 100) if total_listings > 0 else 0

        # Calculate total ROI
        total_roi = best_roi if best_roi != -float('inf') else 0

        result = {
            "total_roi": total_roi,
            "best_performing_team": best_team,
            "worst_performing_team": worst_team,
            "avg_sale_time": avg_sale_time,
            "success_rate": overall_success_rate,
            "team_metrics": team_metrics
        }
        
        logger.info(f"User performance calculated: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error calculating user performance: {e}")
        raise HTTPException(status_code=500, detail="Error calculating user performance")

# Phase 2 AI Analytics Endpoints

@router.get("/ai-insights")
async def get_ai_insights(
    user_id: str = None,
    include_predictions: bool = True,
    include_recommendations: bool = True,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get comprehensive AI-driven insights for user portfolio
    
    Provides AI-generated analysis including market predictions,
    optimization recommendations, and strategic insights.
    """
    try:
        from app.services.ai_service import AIService
        
        logger.info(f"Generating AI insights for user: {user_id}")
        
        # Default to first user if no user_id provided
        if not user_id:
            user_result = await db.execute(select(User).limit(1))
            user = user_result.scalar_one_or_none()
            if user:
                user_id = str(user.id)
            else:
                return {"error": "No users found"}
        
        ai_service = AIService()
        
        # Generate comprehensive AI insights
        insights = await ai_service.generate_portfolio_insights(
            user_id=user_id,
            db=db
        )
        
        # Add market sentiment analysis for user's teams
        team_sentiments = {}
        
        # Get user's teams
        teams_result = await db.execute(
            select(SeasonTicket.team)
            .where(SeasonTicket.user_id == user_id)
            .distinct()
        )
        teams = [row[0] for row in teams_result.fetchall()]
        
        # Get sentiment for each team
        for team in teams[:3]:  # Limit to 3 teams for performance
            try:
                sentiment = await ai_service.analyze_market_sentiment(team, db)
                team_sentiments[team] = sentiment
            except Exception as e:
                logger.warning(f"Could not get sentiment for {team}: {e}")
        
        result = {
            "ai_insights": insights,
            "market_sentiment": team_sentiments,
            "generated_at": datetime.now().isoformat(),
            "user_id": user_id
        }
        
        # Filter based on request parameters
        if not include_predictions:
            result.pop("market_sentiment", None)
        if not include_recommendations:
            if "ai_insights" in result:
                result["ai_insights"].pop("recommendations", None)
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating AI insights: {e}")
        raise HTTPException(status_code=500, detail="Error generating AI insights")

@router.get("/predictive-analytics")
async def get_predictive_analytics(
    user_id: str = None,
    forecast_days: int = 30,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get predictive analytics and forecasting for portfolio performance
    
    Uses AI to predict market trends, optimal selling times,
    and portfolio value projections.
    """
    try:
        from app.services.ai_service import AIService
        
        logger.info(f"Generating predictive analytics for user: {user_id}, forecast: {forecast_days} days")
        
        # Default to first user if no user_id provided  
        if not user_id:
            user_result = await db.execute(select(User).limit(1))
            user = user_result.scalar_one_or_none()
            if user:
                user_id = str(user.id)
            else:
                return {"error": "No users found"}
        
        ai_service = AIService()
        
        # Get user's active listings for prediction
        active_listings_result = await db.execute(
            select(Listing, SeasonTicket)
            .join(SeasonTicket, Listing.season_ticket_id == SeasonTicket.id)
            .where(
                and_(
                    SeasonTicket.user_id == user_id,
                    Listing.status == 'active'
                )
            )
            .limit(10)  # Limit for performance
        )
        
        active_listings = active_listings_result.fetchall()
        
        # Generate predictions for each listing
        price_predictions = []
        total_predicted_value = 0
        
        for listing, season_ticket in active_listings:
            try:
                # Build ticket data for prediction
                ticket_data = {
                    "team": season_ticket.team_name,
                    "venue": season_ticket.venue,
                    "section": listing.section,
                    "row": listing.row,
                    "seat_count": listing.quantity,
                    "current_price": listing.price,
                    "game_date": listing.game_date.isoformat() if listing.game_date else ""
                }
                
                # Get AI price prediction
                prediction = await ai_service.predict_ticket_price(
                    ticket_data=ticket_data,
                    db=db
                )
                
                prediction_data = {
                    "listing_id": str(listing.id),
                    "team": season_ticket.team_name,
                    "current_price": listing.price,
                    "predicted_price": prediction.get("predicted_price", 0),
                    "confidence": prediction.get("confidence", 0),
                    "potential_gain": prediction.get("predicted_price", 0) - listing.price
                }
                
                price_predictions.append(prediction_data)
                total_predicted_value += prediction.get("predicted_price", 0)
                
            except Exception as e:
                logger.warning(f"Could not predict price for listing {listing.id}: {e}")
        
        # Calculate portfolio-level predictions
        current_total_value = sum([listing.price for listing, _ in active_listings])
        predicted_change = total_predicted_value - current_total_value
        predicted_change_percent = (predicted_change / current_total_value * 100) if current_total_value > 0 else 0
        
        result = {
            "forecast_period_days": forecast_days,
            "price_predictions": price_predictions,
            "portfolio_forecast": {
                "current_value": current_total_value,
                "predicted_value": total_predicted_value,
                "predicted_change": predicted_change,
                "predicted_change_percent": predicted_change_percent
            },
            "confidence_score": sum([p["confidence"] for p in price_predictions]) / len(price_predictions) if price_predictions else 0,
            "generated_at": datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating predictive analytics: {e}")
        raise HTTPException(status_code=500, detail="Error generating predictive analytics")

@router.get("/optimization-recommendations")
async def get_optimization_recommendations(
    user_id: str = None,
    focus_area: str = "all",  # "pricing", "timing", "portfolio", "all"
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get AI-powered optimization recommendations for ticket portfolio
    
    Provides specific, actionable recommendations for improving
    portfolio performance, pricing strategies, and market timing.
    """
    try:
        from app.services.ai_service import AIService
        
        logger.info(f"Generating optimization recommendations for user: {user_id}")
        
        # Default to first user if no user_id provided
        if not user_id:
            user_result = await db.execute(select(User).limit(1))
            user = user_result.scalar_one_or_none()
            if user:
                user_id = str(user.id)
            else:
                return {"error": "No users found"}
        
        ai_service = AIService()
        
        # Get user portfolio insights
        insights = await ai_service.generate_portfolio_insights(user_id, db)
        
        # Get current listings for pricing recommendations
        listings_result = await db.execute(
            select(Listing, SeasonTicket)
            .join(SeasonTicket, Listing.season_ticket_id == SeasonTicket.id)
            .where(
                and_(
                    SeasonTicket.user_id == user_id,
                    Listing.status == 'active'
                )
            )
            .limit(5)
        )
        
        listings = listings_result.fetchall()
        pricing_recommendations = []
        
        for listing, season_ticket in listings:
            try:
                listing_data = {
                    "listing_id": str(listing.id),
                    "team": season_ticket.team_name,
                    "section": listing.section,
                    "current_price": listing.price,
                    "days_listed": (datetime.now() - listing.created_at).days,
                    "game_date": listing.game_date.isoformat() if listing.game_date else ""
                }
                
                pricing_rec = await ai_service.generate_smart_pricing_recommendation(
                    listing_data=listing_data,
                    db=db
                )
                
                pricing_recommendations.append({
                    "listing_id": str(listing.id),
                    "team": season_ticket.team_name,
                    "current_price": listing.price,
                    "recommendation": pricing_rec
                })
                
            except Exception as e:
                logger.warning(f"Could not generate pricing rec for listing {listing.id}: {e}")
        
        # Build comprehensive recommendations
        result = {
            "focus_area": focus_area,
            "portfolio_insights": insights.get("recommendations", []),
            "pricing_recommendations": pricing_recommendations,
            "strategic_recommendations": [
                "Consider diversifying across multiple teams to reduce risk",
                "Monitor market sentiment before major games for optimal timing",
                "Adjust prices based on team performance and playoff scenarios",
                "Use historical data to identify seasonal patterns"
            ],
            "priority_actions": insights.get("alerts", []),
            "generated_at": datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating optimization recommendations: {e}")
        raise HTTPException(status_code=500, detail="Error generating optimization recommendations") 