"""
Advanced Feature Engineering Framework for SeatSync Phase 1
AI Foundation & Data Pipeline Implementation

This service provides comprehensive feature engineering capabilities including:
- Market features (price volatility, listing density, etc.)
- Team performance features (win rate, opponent strength, etc.)
- Temporal features (seasonality, time-based patterns)
- External features (weather, sentiment, competition)
- Historical features (patterns, elasticity, seasonal trends)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, text, func

from app.models.database import Listing, SeasonTicket, MarketData, SentimentData

logger = logging.getLogger(__name__)

class FeatureEngineering:
    """
    Advanced Feature Engineering System
    Implements comprehensive feature extraction for ML models
    """
    
    # Comprehensive feature set as defined in the roadmap
    FEATURE_CATEGORIES = {
        'market_features': [
            'current_market_price', 'price_volatility', 'listing_density',
            'price_trend_7d', 'price_trend_30d', 'supply_demand_ratio',
            'competitor_price_diff', 'market_share', 'liquidity_score'
        ],
        'team_performance_features': [
            'team_win_rate', 'opponent_strength', 'playoff_probability',
            'recent_form', 'home_advantage', 'head_to_head_record',
            'scoring_average', 'defensive_rating', 'injury_impact'
        ],
        'temporal_features': [
            'days_until_game', 'hour_of_day', 'day_of_week', 'season_progress',
            'holiday_proximity', 'weekend_indicator', 'prime_time_indicator',
            'season_type', 'time_since_announcement', 'listing_age'
        ],
        'external_features': [
            'weather_score', 'event_competition', 'media_coverage',
            'travel_difficulty', 'economic_indicators', 'fan_sentiment_score',
            'social_media_buzz', 'news_sentiment', 'promotional_activity'
        ],
        'sentiment_features': [
            'fan_sentiment', 'injury_impact', 'rivalry_score',
            'player_popularity', 'team_momentum', 'controversy_factor',
            'excitement_level', 'expectation_index', 'media_attention'
        ],
        'historical_features': [
            'historical_demand', 'price_elasticity', 'seasonal_patterns',
            'similar_game_performance', 'venue_premium', 'section_popularity',
            'repeat_buyer_rate', 'cancellation_rate', 'last_minute_premium'
        ]
    }
    
    def __init__(self):
        self.feature_processors = {
            'market': MarketFeatureEngineer(),
            'team': TeamFeatureEngineer(),
            'temporal': TemporalFeatureEngineer(),
            'external': ExternalFeatureEngineer(),
            'sentiment': SentimentFeatureEngineer(),
            'historical': HistoricalFeatureEngineer()
        }
    
    async def engineer_features(
        self, 
        ticket_data: Dict[str, Any], 
        db: AsyncSession,
        feature_categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Engineer comprehensive features for a ticket listing
        
        Args:
            ticket_data: Raw ticket information
            db: Database session
            feature_categories: Specific categories to process (default: all)
            
        Returns:
            Dictionary of engineered features
        """
        try:
            if feature_categories is None:
                feature_categories = list(self.feature_processors.keys())
            
            features = {}
            
            # Process each feature category
            for category in feature_categories:
                if category in self.feature_processors:
                    processor = self.feature_processors[category]
                    category_features = await processor.process(ticket_data, db)
                    features.update(category_features)
            
            # Calculate derived features
            derived_features = await self._calculate_derived_features(features, db)
            features.update(derived_features)
            
            # Normalize and scale features
            normalized_features = await self._normalize_features(features)
            features.update(normalized_features)
            
            return features
            
        except Exception as e:
            logger.error(f"Feature engineering error: {e}")
            return {}
    
    async def _calculate_derived_features(
        self, 
        features: Dict[str, Any], 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Calculate derived features from base features"""
        derived = {}
        
        try:
            # Price momentum features
            if 'price_trend_7d' in features and 'price_trend_30d' in features:
                derived['price_momentum'] = (
                    features['price_trend_7d'] - features['price_trend_30d']
                )
            
            # Team strength differential
            if 'team_win_rate' in features and 'opponent_strength' in features:
                derived['strength_differential'] = (
                    features['team_win_rate'] - features['opponent_strength']
                )
            
            # Demand pressure index
            if 'listing_density' in features and 'days_until_game' in features:
                derived['demand_pressure'] = (
                    features['listing_density'] / max(features['days_until_game'], 1)
                )
            
            # Sentiment-performance alignment
            if 'fan_sentiment' in features and 'recent_form' in features:
                derived['sentiment_performance_alignment'] = (
                    features['fan_sentiment'] * features['recent_form']
                )
            
            return derived
            
        except Exception as e:
            logger.error(f"Derived features calculation error: {e}")
            return {}
    
    async def _normalize_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize features for ML model consumption"""
        normalized = {}
        
        try:
            # Define normalization rules for different feature types
            percentage_features = [
                'team_win_rate', 'opponent_strength', 'playoff_probability',
                'price_volatility', 'fan_sentiment'
            ]
            
            for feature_name, value in features.items():
                if isinstance(value, (int, float)):
                    if feature_name in percentage_features:
                        # Ensure percentage features are between 0 and 1
                        normalized[f"{feature_name}_normalized"] = max(0, min(1, value))
                    elif feature_name.endswith('_score'):
                        # Score features typically 0-100, normalize to 0-1
                        normalized[f"{feature_name}_normalized"] = value / 100.0
                    elif feature_name.startswith('days_'):
                        # Time-based features, apply log transformation
                        normalized[f"{feature_name}_log"] = np.log1p(max(0, value))
            
            return normalized
            
        except Exception as e:
            logger.error(f"Feature normalization error: {e}")
            return {}


class MarketFeatureEngineer:
    """Market-specific feature engineering"""
    
    async def process(self, ticket_data: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Process market-related features"""
        try:
            features = {}
            
            team = ticket_data.get('team', '')
            venue = ticket_data.get('venue', '')
            section = ticket_data.get('section', '')
            game_date = ticket_data.get('game_date')
            
            # Current market price analysis
            features['current_market_price'] = await self._get_current_market_price(
                db, team, venue, section, game_date
            )
            
            # Price volatility
            features['price_volatility'] = await self._calculate_price_volatility(
                db, team, venue, section
            )
            
            # Listing density
            features['listing_density'] = await self._calculate_listing_density(
                db, team, venue, game_date
            )
            
            # Price trends
            features['price_trend_7d'] = await self._calculate_price_trend(
                db, team, venue, section, days=7
            )
            features['price_trend_30d'] = await self._calculate_price_trend(
                db, team, venue, section, days=30
            )
            
            # Supply-demand ratio
            features['supply_demand_ratio'] = await self._calculate_supply_demand_ratio(
                db, team, venue, game_date
            )
            
            return features
            
        except Exception as e:
            logger.error(f"Market feature engineering error: {e}")
            return {}
    
    async def _get_current_market_price(
        self, 
        db: AsyncSession, 
        team: str, 
        venue: str, 
        section: str, 
        game_date: datetime
    ) -> float:
        """Get current market price for similar tickets"""
        try:
            query = text("""
                SELECT AVG(l.price) as avg_price
                FROM listings l
                JOIN season_tickets st ON l.season_ticket_id = st.id
                WHERE st.team LIKE :team 
                  AND st.venue LIKE :venue
                  AND l.section LIKE :section
                  AND l.status = 'active'
                  AND l.game_date BETWEEN :start_date AND :end_date
            """)
            
            result = await db.execute(query, {
                "team": f"%{team}%",
                "venue": f"%{venue}%", 
                "section": f"%{section}%",
                "start_date": game_date - timedelta(days=7),
                "end_date": game_date + timedelta(days=7)
            })
            
            row = result.fetchone()
            return float(row[0]) if row and row[0] else 0.0
            
        except Exception as e:
            logger.error(f"Current market price calculation error: {e}")
            return 0.0
    
    async def _calculate_price_volatility(
        self, 
        db: AsyncSession, 
        team: str, 
        venue: str, 
        section: str
    ) -> float:
        """Calculate price volatility for similar tickets"""
        try:
            query = text("""
                SELECT STDDEV(l.price) as price_stddev, AVG(l.price) as avg_price
                FROM listings l
                JOIN season_tickets st ON l.season_ticket_id = st.id
                WHERE st.team LIKE :team 
                  AND st.venue LIKE :venue
                  AND l.section LIKE :section
                  AND l.created_at >= date('now', '-30 days')
            """)
            
            result = await db.execute(query, {
                "team": f"%{team}%",
                "venue": f"%{venue}%",
                "section": f"%{section}%"
            })
            
            row = result.fetchone()
            if row and row[0] and row[1]:
                # Coefficient of variation (volatility)
                return float(row[0]) / float(row[1])
            return 0.0
            
        except Exception as e:
            logger.error(f"Price volatility calculation error: {e}")
            return 0.0
    
    async def _calculate_listing_density(
        self, 
        db: AsyncSession, 
        team: str, 
        venue: str, 
        game_date: datetime
    ) -> float:
        """Calculate listing density for the game"""
        try:
            query = text("""
                SELECT COUNT(*) as listing_count
                FROM listings l
                JOIN season_tickets st ON l.season_ticket_id = st.id
                WHERE st.team LIKE :team 
                  AND st.venue LIKE :venue
                  AND l.game_date = :game_date
                  AND l.status = 'active'
            """)
            
            result = await db.execute(query, {
                "team": f"%{team}%",
                "venue": f"%{venue}%",
                "game_date": game_date
            })
            
            row = result.fetchone()
            return float(row[0]) if row else 0.0
            
        except Exception as e:
            logger.error(f"Listing density calculation error: {e}")
            return 0.0
    
    async def _calculate_price_trend(
        self, 
        db: AsyncSession, 
        team: str, 
        venue: str, 
        section: str, 
        days: int
    ) -> float:
        """Calculate price trend over specified period"""
        try:
            query = text("""
                SELECT 
                    AVG(CASE WHEN l.created_at >= date('now', '-' || :half_days || ' days') 
                        THEN l.price END) as recent_avg,
                    AVG(CASE WHEN l.created_at < date('now', '-' || :half_days || ' days') 
                        THEN l.price END) as older_avg
                FROM listings l
                JOIN season_tickets st ON l.season_ticket_id = st.id
                WHERE st.team LIKE :team 
                  AND st.venue LIKE :venue
                  AND l.section LIKE :section
                  AND l.created_at >= date('now', '-' || :total_days || ' days')
            """)
            
            result = await db.execute(query, {
                "team": f"%{team}%",
                "venue": f"%{venue}%",
                "section": f"%{section}%",
                "half_days": days // 2,
                "total_days": days
            })
            
            row = result.fetchone()
            if row and row[0] and row[1]:
                # Percentage change
                return (float(row[0]) - float(row[1])) / float(row[1])
            return 0.0
            
        except Exception as e:
            logger.error(f"Price trend calculation error: {e}")
            return 0.0
    
    async def _calculate_supply_demand_ratio(
        self, 
        db: AsyncSession, 
        team: str, 
        venue: str, 
        game_date: datetime
    ) -> float:
        """Calculate supply-demand ratio"""
        try:
            # This is a simplified implementation
            # In practice, you'd need more sophisticated demand indicators
            supply_query = text("""
                SELECT COUNT(*) as supply
                FROM listings l
                JOIN season_tickets st ON l.season_ticket_id = st.id
                WHERE st.team LIKE :team 
                  AND st.venue LIKE :venue
                  AND l.game_date = :game_date
                  AND l.status = 'active'
            """)
            
            demand_query = text("""
                SELECT COUNT(*) as demand
                FROM listings l
                JOIN season_tickets st ON l.season_ticket_id = st.id
                WHERE st.team LIKE :team 
                  AND st.venue LIKE :venue
                  AND l.game_date = :game_date
                  AND l.status = 'sold'
                  AND l.sold_at >= date('now', '-7 days')
            """)
            
            supply_result = await db.execute(supply_query, {
                "team": f"%{team}%",
                "venue": f"%{venue}%",
                "game_date": game_date
            })
            
            demand_result = await db.execute(demand_query, {
                "team": f"%{team}%",
                "venue": f"%{venue}%",
                "game_date": game_date
            })
            
            supply = supply_result.fetchone()[0] or 0
            demand = demand_result.fetchone()[0] or 0
            
            if demand > 0:
                return supply / demand
            return supply  # If no demand, return raw supply
            
        except Exception as e:
            logger.error(f"Supply-demand ratio calculation error: {e}")
            return 0.0


class TeamFeatureEngineer:
    """Team performance feature engineering"""
    
    async def process(self, ticket_data: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Process team performance features"""
        try:
            features = {}
            
            team = ticket_data.get('team', '')
            opponent = ticket_data.get('opponent', '')
            
            # Team win rate
            features['team_win_rate'] = await self._get_team_win_rate(db, team)
            
            # Opponent strength
            features['opponent_strength'] = await self._get_team_win_rate(db, opponent)
            
            # Playoff probability (mock implementation)
            features['playoff_probability'] = await self._calculate_playoff_probability(db, team)
            
            # Recent form
            features['recent_form'] = await self._get_recent_form(db, team)
            
            # Home advantage
            features['home_advantage'] = await self._calculate_home_advantage(db, team)
            
            return features
            
        except Exception as e:
            logger.error(f"Team feature engineering error: {e}")
            return {}
    
    async def _get_team_win_rate(self, db: AsyncSession, team: str) -> float:
        """Get team win rate from stored data"""
        try:
            # Mock implementation - would integrate with sports data
            query = text("""
                SELECT data
                FROM market_data
                WHERE team LIKE :team
                  AND data_type = 'team_stats'
                ORDER BY created_at DESC
                LIMIT 1
            """)
            
            result = await db.execute(query, {"team": f"%{team}%"})
            row = result.fetchone()
            
            if row and row[0]:
                data = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                return data.get('win_rate', 0.5)  # Default to 50%
            
            return 0.5  # Default win rate
            
        except Exception as e:
            logger.error(f"Team win rate calculation error: {e}")
            return 0.5
    
    async def _calculate_playoff_probability(self, db: AsyncSession, team: str) -> float:
        """Calculate playoff probability"""
        # Mock implementation
        return 0.5
    
    async def _get_recent_form(self, db: AsyncSession, team: str) -> float:
        """Get recent team form"""
        # Mock implementation
        return 0.5
    
    async def _calculate_home_advantage(self, db: AsyncSession, team: str) -> float:
        """Calculate home field advantage"""
        # Mock implementation
        return 0.1


class TemporalFeatureEngineer:
    """Temporal feature engineering"""
    
    async def process(self, ticket_data: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Process temporal features"""
        try:
            features = {}
            
            game_date = ticket_data.get('game_date')
            listed_date = ticket_data.get('listed_date', datetime.utcnow())
            
            if game_date:
                # Days until game
                features['days_until_game'] = (game_date - datetime.utcnow()).days
                
                # Hour of day
                features['hour_of_day'] = game_date.hour
                
                # Day of week (0=Monday, 6=Sunday)
                features['day_of_week'] = game_date.weekday()
                
                # Weekend indicator
                features['weekend_indicator'] = 1 if game_date.weekday() >= 5 else 0
                
                # Prime time indicator (7-10 PM)
                features['prime_time_indicator'] = 1 if 19 <= game_date.hour <= 22 else 0
                
                # Season progress (mock implementation)
                features['season_progress'] = self._calculate_season_progress(game_date)
                
                # Listing age
                features['listing_age'] = (datetime.utcnow() - listed_date).days
            
            return features
            
        except Exception as e:
            logger.error(f"Temporal feature engineering error: {e}")
            return {}
    
    def _calculate_season_progress(self, game_date: datetime) -> float:
        """Calculate how far into the season the game is"""
        # Mock implementation - would depend on league and season structure
        month = game_date.month
        if month in [10, 11, 12, 1, 2, 3]:  # NBA/NHL season
            return (month - 10) / 6.0 if month >= 10 else (month + 2) / 6.0
        elif month in [4, 5, 6, 7, 8, 9]:  # MLB season
            return (month - 4) / 6.0
        else:  # NFL season
            return (month - 9) / 4.0 if month >= 9 else 1.0


class ExternalFeatureEngineer:
    """External context feature engineering"""
    
    async def process(self, ticket_data: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Process external context features"""
        try:
            features = {}
            
            # Weather score (mock implementation)
            features['weather_score'] = await self._get_weather_score(ticket_data)
            
            # Event competition (mock implementation)
            features['event_competition'] = await self._get_competing_events_score(ticket_data)
            
            # Media coverage (mock implementation)
            features['media_coverage'] = await self._get_media_coverage_score(ticket_data)
            
            return features
            
        except Exception as e:
            logger.error(f"External feature engineering error: {e}")
            return {}
    
    async def _get_weather_score(self, ticket_data: Dict[str, Any]) -> float:
        """Get weather favorability score"""
        # Mock implementation
        return 0.8
    
    async def _get_competing_events_score(self, ticket_data: Dict[str, Any]) -> float:
        """Get competing events impact score"""
        # Mock implementation
        return 0.3
    
    async def _get_media_coverage_score(self, ticket_data: Dict[str, Any]) -> float:
        """Get media coverage intensity score"""
        # Mock implementation
        return 0.6


class SentimentFeatureEngineer:
    """Sentiment-based feature engineering"""
    
    async def process(self, ticket_data: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Process sentiment features"""
        try:
            features = {}
            
            team = ticket_data.get('team', '')
            
            # Fan sentiment
            features['fan_sentiment'] = await self._get_fan_sentiment(db, team)
            
            # Rivalry score
            features['rivalry_score'] = await self._get_rivalry_score(ticket_data)
            
            # Injury impact
            features['injury_impact'] = await self._get_injury_impact(db, team)
            
            return features
            
        except Exception as e:
            logger.error(f"Sentiment feature engineering error: {e}")
            return {}
    
    async def _get_fan_sentiment(self, db: AsyncSession, team: str) -> float:
        """Get current fan sentiment for team"""
        try:
            query = text("""
                SELECT AVG(sentiment_score) as avg_sentiment
                FROM sentiment_data
                WHERE team LIKE :team
                  AND created_at >= date('now', '-7 days')
            """)
            
            result = await db.execute(query, {"team": f"%{team}%"})
            row = result.fetchone()
            
            return float(row[0]) if row and row[0] else 0.5
            
        except Exception as e:
            logger.error(f"Fan sentiment calculation error: {e}")
            return 0.5
    
    async def _get_rivalry_score(self, ticket_data: Dict[str, Any]) -> float:
        """Calculate rivalry intensity score"""
        # Mock implementation
        return 0.5
    
    async def _get_injury_impact(self, db: AsyncSession, team: str) -> float:
        """Calculate injury impact on team performance"""
        # Mock implementation
        return 0.2


class HistoricalFeatureEngineer:
    """Historical pattern feature engineering"""
    
    async def process(self, ticket_data: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Process historical features"""
        try:
            features = {}
            
            # Historical demand patterns
            features['historical_demand'] = await self._get_historical_demand(db, ticket_data)
            
            # Price elasticity
            features['price_elasticity'] = await self._calculate_price_elasticity(db, ticket_data)
            
            # Seasonal patterns
            features['seasonal_patterns'] = await self._get_seasonal_patterns(db, ticket_data)
            
            return features
            
        except Exception as e:
            logger.error(f"Historical feature engineering error: {e}")
            return {}
    
    async def _get_historical_demand(self, db: AsyncSession, ticket_data: Dict[str, Any]) -> float:
        """Get historical demand for similar games"""
        # Mock implementation
        return 0.7
    
    async def _calculate_price_elasticity(self, db: AsyncSession, ticket_data: Dict[str, Any]) -> float:
        """Calculate price elasticity of demand"""
        # Mock implementation
        return -0.8
    
    async def _get_seasonal_patterns(self, db: AsyncSession, ticket_data: Dict[str, Any]) -> float:
        """Get seasonal demand patterns"""
        # Mock implementation
        return 0.6