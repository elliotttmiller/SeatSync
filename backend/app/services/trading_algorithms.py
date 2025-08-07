"""
Advanced Trading Algorithms for SeatSync Phase 3
Sophisticated Trading Strategies and Portfolio Optimization

This service provides advanced trading capabilities including:
- Momentum and Mean Reversion strategies
- Arbitrage detection across platforms
- Market making strategies
- Modern Portfolio Theory for tickets
- Risk-adjusted position sizing
- Multi-platform execution
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

# Financial optimization imports
try:
    import scipy.optimize as sco
    from scipy.stats import norm
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, text, func

from app.core.config import settings
from app.models.database import Listing, SeasonTicket, AutomationRule, MarketplaceAccount
from app.services.ensemble_models import EnsemblePricingModel

logger = logging.getLogger(__name__)

class TradeSignal(Enum):
    """Trade signal types"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

@dataclass
class TradeRecommendation:
    """Structured trade recommendation"""
    signal: TradeSignal
    confidence: float
    target_price: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    position_size: float
    reasoning: str
    risk_metrics: Dict[str, float]
    time_horizon: str

@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics"""
    total_value: float
    unrealized_pnl: float
    realized_pnl: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    volatility: float
    beta: float
    alpha: float
    var_95: float  # Value at Risk 95%
    expected_shortfall: float

class AdvancedTradingEngine:
    """
    Sophisticated Trading Strategies Engine
    Implements multiple algorithmic trading strategies for ticket portfolios
    """
    
    def __init__(self):
        self.strategies = {
            'momentum_trading': MomentumStrategy(),
            'mean_reversion': MeanReversionStrategy(),
            'arbitrage_detection': ArbitrageStrategy(),
            'market_making': MarketMakingStrategy(),
            'portfolio_optimization': PortfolioOptimizer()
        }
        self.ensemble_model = EnsemblePricingModel()
        self.risk_manager = AdvancedRiskManagement()
        
    async def execute_strategy(
        self, 
        strategy_name: str, 
        portfolio_data: Dict[str, Any],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Execute advanced trading strategies with risk management
        
        Args:
            strategy_name: Name of strategy to execute
            portfolio_data: Current portfolio information
            db: Database session
            
        Returns:
            Strategy execution results with trade recommendations
        """
        try:
            if strategy_name not in self.strategies:
                return {"error": f"Strategy {strategy_name} not found"}
            
            strategy = self.strategies[strategy_name]
            
            logger.info(f"Executing strategy: {strategy_name}")
            
            # 1. Real-time market analysis
            market_analysis = await self._analyze_market_conditions(db)
            
            # 2. Generate strategy signals
            signals = await strategy.generate_signals(portfolio_data, market_analysis, db)
            
            # 3. Risk-adjusted position sizing
            risk_adjusted_signals = await self.risk_manager.adjust_position_sizes(
                signals, portfolio_data, db
            )
            
            # 4. Multi-platform execution planning
            execution_plan = await self._plan_multi_platform_execution(
                risk_adjusted_signals, db
            )
            
            # 5. Performance attribution
            attribution = await self._calculate_performance_attribution(
                strategy_name, portfolio_data, db
            )
            
            return {
                "strategy": strategy_name,
                "status": "completed",
                "signals": [signal.__dict__ for signal in risk_adjusted_signals],
                "execution_plan": execution_plan,
                "market_analysis": market_analysis,
                "performance_attribution": attribution,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Strategy execution error: {e}")
            return {"error": str(e), "strategy": strategy_name}
    
    async def _analyze_market_conditions(self, db: AsyncSession) -> Dict[str, Any]:
        """Comprehensive real-time market analysis"""
        try:
            # Market trend analysis
            trend_analysis = await self._analyze_market_trends(db)
            
            # Volatility analysis
            volatility_metrics = await self._calculate_volatility_metrics(db)
            
            # Liquidity analysis
            liquidity_metrics = await self._analyze_market_liquidity(db)
            
            # Sentiment analysis
            sentiment_metrics = await self._analyze_market_sentiment(db)
            
            return {
                "trends": trend_analysis,
                "volatility": volatility_metrics,
                "liquidity": liquidity_metrics,
                "sentiment": sentiment_metrics,
                "overall_score": self._calculate_market_score(
                    trend_analysis, volatility_metrics, liquidity_metrics, sentiment_metrics
                )
            }
            
        except Exception as e:
            logger.error(f"Market analysis error: {e}")
            return {}
    
    async def _analyze_market_trends(self, db: AsyncSession) -> Dict[str, Any]:
        """Analyze market trends across different time horizons"""
        try:
            query = text("""
                SELECT 
                    DATE(l.created_at) as date,
                    AVG(l.price) as avg_price,
                    COUNT(*) as volume,
                    STDDEV(l.price) as price_std
                FROM listings l
                WHERE l.created_at >= date('now', '-30 days')
                  AND l.status IN ('active', 'sold')
                GROUP BY DATE(l.created_at)
                ORDER BY date DESC
                LIMIT 30
            """)
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            if not rows:
                return {"trend": "neutral", "strength": 0.0}
            
            # Calculate trend metrics
            prices = [float(row[1]) for row in rows]
            volumes = [int(row[2]) for row in rows]
            
            # Price trend (linear regression slope)
            x = np.arange(len(prices))
            if len(prices) > 1:
                price_trend = np.polyfit(x, prices, 1)[0]  # Slope
                volume_trend = np.polyfit(x, volumes, 1)[0] if len(volumes) > 1 else 0
            else:
                price_trend = 0
                volume_trend = 0
            
            return {
                "price_trend": float(price_trend),
                "volume_trend": float(volume_trend),
                "trend_direction": "bullish" if price_trend > 0 else "bearish" if price_trend < 0 else "neutral",
                "trend_strength": min(abs(price_trend) / np.mean(prices) * 100, 100) if prices else 0
            }
            
        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
            return {"trend": "neutral", "strength": 0.0}
    
    async def _calculate_volatility_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Calculate comprehensive volatility metrics"""
        try:
            query = text("""
                SELECT 
                    l.price,
                    l.created_at
                FROM listings l
                WHERE l.created_at >= date('now', '-30 days')
                  AND l.status IN ('active', 'sold')
                ORDER BY l.created_at
            """)
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            if len(rows) < 2:
                return {"volatility": 0.0, "regime": "low"}
            
            prices = [float(row[0]) for row in rows]
            
            # Calculate returns
            returns = [
                (prices[i] - prices[i-1]) / prices[i-1] 
                for i in range(1, len(prices))
                if prices[i-1] != 0
            ]
            
            if not returns:
                return {"volatility": 0.0, "regime": "low"}
            
            # Volatility metrics
            volatility = np.std(returns) * np.sqrt(252)  # Annualized
            realized_vol = np.std(returns[-7:]) * np.sqrt(252) if len(returns) >= 7 else volatility
            
            # Volatility regime
            vol_regime = "high" if volatility > 0.3 else "medium" if volatility > 0.15 else "low"
            
            return {
                "volatility": float(volatility),
                "realized_volatility": float(realized_vol),
                "volatility_regime": vol_regime,
                "vol_of_vol": float(np.std([np.std(returns[max(0, i-7):i]) for i in range(7, len(returns))]))
            }
            
        except Exception as e:
            logger.error(f"Volatility calculation error: {e}")
            return {"volatility": 0.0, "regime": "low"}
    
    async def _analyze_market_liquidity(self, db: AsyncSession) -> Dict[str, Any]:
        """Analyze market liquidity conditions"""
        try:
            # Active listings vs. sales ratio
            active_query = text("""
                SELECT COUNT(*) as active_count
                FROM listings l
                WHERE l.status = 'active'
                  AND l.created_at >= date('now', '-7 days')
            """)
            
            sold_query = text("""
                SELECT COUNT(*) as sold_count
                FROM listings l
                WHERE l.status = 'sold'
                  AND l.sold_at >= date('now', '-7 days')
            """)
            
            active_result = await db.execute(active_query)
            sold_result = await db.execute(sold_query)
            
            active_count = active_result.fetchone()[0] or 0
            sold_count = sold_result.fetchone()[0] or 0
            
            # Liquidity metrics
            liquidity_ratio = sold_count / max(active_count, 1)
            
            # Average time to sale
            time_to_sale_query = text("""
                SELECT AVG(julianday(l.sold_at) - julianday(l.created_at)) as avg_days
                FROM listings l
                WHERE l.status = 'sold'
                  AND l.sold_at >= date('now', '-30 days')
            """)
            
            time_result = await db.execute(time_to_sale_query)
            avg_time_to_sale = time_result.fetchone()[0] or 0
            
            # Liquidity score
            liquidity_score = min(100, liquidity_ratio * 50 + (1 / max(avg_time_to_sale, 0.1)) * 10)
            
            return {
                "liquidity_ratio": float(liquidity_ratio),
                "avg_time_to_sale": float(avg_time_to_sale),
                "liquidity_score": float(liquidity_score),
                "liquidity_regime": "high" if liquidity_score > 70 else "medium" if liquidity_score > 40 else "low"
            }
            
        except Exception as e:
            logger.error(f"Liquidity analysis error: {e}")
            return {"liquidity_score": 50.0, "liquidity_regime": "medium"}
    
    async def _analyze_market_sentiment(self, db: AsyncSession) -> Dict[str, Any]:
        """Analyze overall market sentiment"""
        try:
            # Price momentum as sentiment proxy
            query = text("""
                SELECT 
                    AVG(CASE WHEN l.created_at >= date('now', '-7 days') THEN l.price END) as recent_avg,
                    AVG(CASE WHEN l.created_at < date('now', '-7 days') AND l.created_at >= date('now', '-14 days') THEN l.price END) as older_avg
                FROM listings l
                WHERE l.created_at >= date('now', '-14 days')
                  AND l.status IN ('active', 'sold')
            """)
            
            result = await db.execute(query)
            row = result.fetchone()
            
            if row and row[0] and row[1]:
                price_momentum = (float(row[0]) - float(row[1])) / float(row[1])
            else:
                price_momentum = 0.0
            
            # Convert to sentiment score
            sentiment_score = 50 + (price_momentum * 100)  # Scale around 50
            sentiment_score = max(0, min(100, sentiment_score))
            
            sentiment_label = "bullish" if sentiment_score > 60 else "bearish" if sentiment_score < 40 else "neutral"
            
            return {
                "sentiment_score": float(sentiment_score),
                "sentiment_label": sentiment_label,
                "price_momentum": float(price_momentum)
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {"sentiment_score": 50.0, "sentiment_label": "neutral"}
    
    def _calculate_market_score(
        self, 
        trends: Dict[str, Any], 
        volatility: Dict[str, Any], 
        liquidity: Dict[str, Any], 
        sentiment: Dict[str, Any]
    ) -> float:
        """Calculate overall market favorability score"""
        try:
            trend_score = 50 + trends.get("price_trend", 0) * 10
            vol_score = 100 - volatility.get("volatility", 0) * 100  # Lower volatility is better
            liquidity_score = liquidity.get("liquidity_score", 50)
            sentiment_score = sentiment.get("sentiment_score", 50)
            
            # Weighted average
            overall_score = (
                trend_score * 0.3 +
                vol_score * 0.2 +
                liquidity_score * 0.3 +
                sentiment_score * 0.2
            )
            
            return max(0, min(100, overall_score))
            
        except Exception as e:
            logger.error(f"Market score calculation error: {e}")
            return 50.0
    
    async def _plan_multi_platform_execution(
        self, 
        signals: List[TradeRecommendation], 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Plan execution across multiple platforms"""
        try:
            execution_plan = {
                "total_signals": len(signals),
                "platform_allocation": {},
                "execution_order": [],
                "estimated_slippage": 0.0,
                "total_fees": 0.0
            }
            
            # Analyze platform liquidity and fees
            platforms = ['stubhub', 'seatgeek', 'ticketmaster', 'vivid_seats']
            platform_metrics = {}
            
            for platform in platforms:
                metrics = await self._analyze_platform_metrics(platform, db)
                platform_metrics[platform] = metrics
            
            # Allocate trades to optimal platforms
            for signal in signals:
                best_platform = self._select_optimal_platform(signal, platform_metrics)
                
                if best_platform not in execution_plan["platform_allocation"]:
                    execution_plan["platform_allocation"][best_platform] = 0
                
                execution_plan["platform_allocation"][best_platform] += 1
                execution_plan["execution_order"].append({
                    "signal": signal.signal.value,
                    "platform": best_platform,
                    "target_price": signal.target_price,
                    "position_size": signal.position_size
                })
            
            return execution_plan
            
        except Exception as e:
            logger.error(f"Execution planning error: {e}")
            return {}
    
    async def _analyze_platform_metrics(self, platform: str, db: AsyncSession) -> Dict[str, Any]:
        """Analyze metrics for a specific platform"""
        try:
            query = text("""
                SELECT 
                    COUNT(*) as total_listings,
                    AVG(l.price) as avg_price,
                    COUNT(CASE WHEN l.status = 'sold' THEN 1 END) as sold_count
                FROM listings l
                WHERE l.platform = :platform
                  AND l.created_at >= date('now', '-30 days')
            """)
            
            result = await db.execute(query, {"platform": platform})
            row = result.fetchone()
            
            if row:
                total_listings = row[0] or 0
                avg_price = float(row[1]) if row[1] else 0.0
                sold_count = row[2] or 0
                
                liquidity = sold_count / max(total_listings, 1)
                
                return {
                    "liquidity": liquidity,
                    "avg_price": avg_price,
                    "volume": total_listings,
                    "success_rate": liquidity
                }
            
            return {"liquidity": 0.0, "avg_price": 0.0, "volume": 0, "success_rate": 0.0}
            
        except Exception as e:
            logger.error(f"Platform metrics error for {platform}: {e}")
            return {"liquidity": 0.0, "avg_price": 0.0, "volume": 0, "success_rate": 0.0}
    
    def _select_optimal_platform(
        self, 
        signal: TradeRecommendation, 
        platform_metrics: Dict[str, Dict[str, Any]]
    ) -> str:
        """Select optimal platform for trade execution"""
        try:
            best_platform = "stubhub"  # Default
            best_score = 0.0
            
            for platform, metrics in platform_metrics.items():
                # Score based on liquidity, volume, and success rate
                score = (
                    metrics.get("liquidity", 0) * 0.4 +
                    min(metrics.get("volume", 0) / 100, 1.0) * 0.3 +
                    metrics.get("success_rate", 0) * 0.3
                )
                
                if score > best_score:
                    best_score = score
                    best_platform = platform
            
            return best_platform
            
        except Exception as e:
            logger.error(f"Platform selection error: {e}")
            return "stubhub"
    
    async def _calculate_performance_attribution(
        self, 
        strategy_name: str, 
        portfolio_data: Dict[str, Any], 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Calculate performance attribution for strategy"""
        try:
            # Simplified performance attribution
            return {
                "strategy_contribution": 0.0,
                "alpha": 0.0,
                "beta": 1.0,
                "tracking_error": 0.0,
                "information_ratio": 0.0
            }
            
        except Exception as e:
            logger.error(f"Performance attribution error: {e}")
            return {}


class BaseStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def generate_signals(
        self, 
        portfolio_data: Dict[str, Any], 
        market_analysis: Dict[str, Any], 
        db: AsyncSession
    ) -> List[TradeRecommendation]:
        """Generate trading signals"""
        pass


class MomentumStrategy(BaseStrategy):
    """Momentum-based trading strategy"""
    
    def __init__(self):
        super().__init__("Momentum")
    
    async def generate_signals(
        self, 
        portfolio_data: Dict[str, Any], 
        market_analysis: Dict[str, Any], 
        db: AsyncSession
    ) -> List[TradeRecommendation]:
        """Generate momentum-based signals"""
        try:
            signals = []
            
            # Analyze momentum for each position
            positions = portfolio_data.get("positions", [])
            
            for position in positions:
                momentum_score = await self._calculate_momentum_score(position, db)
                
                if momentum_score > 0.7:  # Strong positive momentum
                    signal = TradeRecommendation(
                        signal=TradeSignal.BUY,
                        confidence=momentum_score,
                        target_price=position.get("current_price", 0) * 1.05,
                        stop_loss=position.get("current_price", 0) * 0.95,
                        take_profit=position.get("current_price", 0) * 1.15,
                        position_size=0.1,  # 10% of portfolio
                        reasoning=f"Strong momentum detected (score: {momentum_score:.2f})",
                        risk_metrics={"momentum_score": momentum_score},
                        time_horizon="short"
                    )
                    signals.append(signal)
                elif momentum_score < 0.3:  # Negative momentum
                    signal = TradeRecommendation(
                        signal=TradeSignal.SELL,
                        confidence=1.0 - momentum_score,
                        target_price=position.get("current_price", 0) * 0.95,
                        stop_loss=None,
                        take_profit=None,
                        position_size=0.5,  # Reduce position by 50%
                        reasoning=f"Negative momentum detected (score: {momentum_score:.2f})",
                        risk_metrics={"momentum_score": momentum_score},
                        time_horizon="immediate"
                    )
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Momentum strategy error: {e}")
            return []
    
    async def _calculate_momentum_score(self, position: Dict[str, Any], db: AsyncSession) -> float:
        """Calculate momentum score for a position"""
        try:
            # Simplified momentum calculation
            # In practice, this would analyze price trends, volume, etc.
            
            team = position.get("team", "")
            venue = position.get("venue", "")
            
            query = text("""
                SELECT 
                    AVG(CASE WHEN l.created_at >= date('now', '-7 days') THEN l.price END) as recent_avg,
                    AVG(CASE WHEN l.created_at < date('now', '-7 days') AND l.created_at >= date('now', '-14 days') THEN l.price END) as older_avg
                FROM listings l
                JOIN season_tickets st ON l.season_ticket_id = st.id
                WHERE st.team LIKE :team
                  AND st.venue LIKE :venue
                  AND l.created_at >= date('now', '-14 days')
            """)
            
            result = await db.execute(query, {"team": f"%{team}%", "venue": f"%{venue}%"})
            row = result.fetchone()
            
            if row and row[0] and row[1]:
                momentum = (float(row[0]) - float(row[1])) / float(row[1])
                # Convert to 0-1 score
                return max(0, min(1, 0.5 + momentum * 2))
            
            return 0.5  # Neutral
            
        except Exception as e:
            logger.error(f"Momentum calculation error: {e}")
            return 0.5


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion trading strategy"""
    
    def __init__(self):
        super().__init__("MeanReversion")
    
    async def generate_signals(
        self, 
        portfolio_data: Dict[str, Any], 
        market_analysis: Dict[str, Any], 
        db: AsyncSession
    ) -> List[TradeRecommendation]:
        """Generate mean reversion signals"""
        try:
            signals = []
            
            positions = portfolio_data.get("positions", [])
            
            for position in positions:
                reversion_signal = await self._calculate_reversion_signal(position, db)
                
                if reversion_signal < -0.2:  # Oversold
                    signal = TradeRecommendation(
                        signal=TradeSignal.BUY,
                        confidence=abs(reversion_signal),
                        target_price=position.get("mean_price", position.get("current_price", 0)),
                        stop_loss=position.get("current_price", 0) * 0.9,
                        take_profit=position.get("mean_price", position.get("current_price", 0)),
                        position_size=0.15,
                        reasoning=f"Mean reversion opportunity - oversold (signal: {reversion_signal:.2f})",
                        risk_metrics={"reversion_signal": reversion_signal},
                        time_horizon="medium"
                    )
                    signals.append(signal)
                elif reversion_signal > 0.2:  # Overbought
                    signal = TradeRecommendation(
                        signal=TradeSignal.SELL,
                        confidence=reversion_signal,
                        target_price=position.get("mean_price", position.get("current_price", 0)),
                        stop_loss=None,
                        take_profit=None,
                        position_size=0.3,
                        reasoning=f"Mean reversion opportunity - overbought (signal: {reversion_signal:.2f})",
                        risk_metrics={"reversion_signal": reversion_signal},
                        time_horizon="medium"
                    )
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Mean reversion strategy error: {e}")
            return []
    
    async def _calculate_reversion_signal(self, position: Dict[str, Any], db: AsyncSession) -> float:
        """Calculate mean reversion signal"""
        try:
            # Calculate deviation from historical mean
            current_price = position.get("current_price", 0)
            mean_price = position.get("mean_price", current_price)
            
            if mean_price == 0:
                return 0.0
            
            # Normalized deviation
            deviation = (current_price - mean_price) / mean_price
            
            return deviation
            
        except Exception as e:
            logger.error(f"Reversion signal calculation error: {e}")
            return 0.0


class ArbitrageStrategy(BaseStrategy):
    """Cross-platform arbitrage detection strategy"""
    
    def __init__(self):
        super().__init__("Arbitrage")
    
    async def generate_signals(
        self, 
        portfolio_data: Dict[str, Any], 
        market_analysis: Dict[str, Any], 
        db: AsyncSession
    ) -> List[TradeRecommendation]:
        """Generate arbitrage signals"""
        try:
            signals = []
            
            # Find arbitrage opportunities across platforms
            arbitrage_opportunities = await self._find_arbitrage_opportunities(db)
            
            for opportunity in arbitrage_opportunities:
                if opportunity["profit_margin"] > 0.05:  # 5% minimum profit
                    # Buy on cheaper platform, sell on expensive platform
                    buy_signal = TradeRecommendation(
                        signal=TradeSignal.BUY,
                        confidence=min(opportunity["profit_margin"] * 10, 1.0),
                        target_price=opportunity["buy_price"],
                        stop_loss=None,
                        take_profit=opportunity["sell_price"],
                        position_size=0.05,  # Small positions for arbitrage
                        reasoning=f"Arbitrage opportunity: {opportunity['profit_margin']:.1%} profit",
                        risk_metrics={"profit_margin": opportunity["profit_margin"]},
                        time_horizon="immediate"
                    )
                    signals.append(buy_signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Arbitrage strategy error: {e}")
            return []
    
    async def _find_arbitrage_opportunities(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Find cross-platform arbitrage opportunities"""
        try:
            # Simplified arbitrage detection
            # In practice, this would compare real-time prices across platforms
            
            query = text("""
                SELECT 
                    st.team,
                    st.venue,
                    l.section,
                    l.platform,
                    MIN(l.price) as min_price,
                    MAX(l.price) as max_price,
                    COUNT(*) as listing_count
                FROM listings l
                JOIN season_tickets st ON l.season_ticket_id = st.id
                WHERE l.status = 'active'
                  AND l.created_at >= date('now', '-1 days')
                GROUP BY st.team, st.venue, l.section, l.platform
                HAVING COUNT(*) >= 2
            """)
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            opportunities = []
            
            # Group by team/venue/section to find price differences
            grouped_data = {}
            for row in rows:
                key = (row[0], row[1], row[2])  # team, venue, section
                if key not in grouped_data:
                    grouped_data[key] = []
                grouped_data[key].append({
                    "platform": row[3],
                    "min_price": float(row[4]),
                    "max_price": float(row[5]),
                    "count": int(row[6])
                })
            
            # Find arbitrage opportunities
            for key, platforms in grouped_data.items():
                if len(platforms) >= 2:
                    min_platform = min(platforms, key=lambda x: x["min_price"])
                    max_platform = max(platforms, key=lambda x: x["max_price"])
                    
                    if min_platform["min_price"] < max_platform["max_price"]:
                        profit_margin = (max_platform["max_price"] - min_platform["min_price"]) / min_platform["min_price"]
                        
                        opportunities.append({
                            "team": key[0],
                            "venue": key[1],
                            "section": key[2],
                            "buy_platform": min_platform["platform"],
                            "sell_platform": max_platform["platform"],
                            "buy_price": min_platform["min_price"],
                            "sell_price": max_platform["max_price"],
                            "profit_margin": profit_margin
                        })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Arbitrage opportunity detection error: {e}")
            return []


class MarketMakingStrategy(BaseStrategy):
    """Market making strategy for providing liquidity"""
    
    def __init__(self):
        super().__init__("MarketMaking")
    
    async def generate_signals(
        self, 
        portfolio_data: Dict[str, Any], 
        market_analysis: Dict[str, Any], 
        db: AsyncSession
    ) -> List[TradeRecommendation]:
        """Generate market making signals"""
        try:
            signals = []
            
            # Identify markets with low liquidity for market making
            illiquid_markets = await self._find_illiquid_markets(db)
            
            for market in illiquid_markets:
                # Provide both buy and sell liquidity
                mid_price = market["estimated_fair_value"]
                spread = market["estimated_spread"]
                
                # Buy order (bid)
                buy_signal = TradeRecommendation(
                    signal=TradeSignal.BUY,
                    confidence=0.6,  # Moderate confidence for market making
                    target_price=mid_price - spread / 2,
                    stop_loss=mid_price - spread,
                    take_profit=mid_price,
                    position_size=0.03,  # Small positions
                    reasoning="Market making - providing bid liquidity",
                    risk_metrics={"spread": spread, "liquidity_score": market["liquidity_score"]},
                    time_horizon="short"
                )
                signals.append(buy_signal)
                
                # Sell order (ask) - if we have inventory
                if portfolio_data.get("has_inventory", False):
                    sell_signal = TradeRecommendation(
                        signal=TradeSignal.SELL,
                        confidence=0.6,
                        target_price=mid_price + spread / 2,
                        stop_loss=None,
                        take_profit=None,
                        position_size=0.03,
                        reasoning="Market making - providing ask liquidity",
                        risk_metrics={"spread": spread, "liquidity_score": market["liquidity_score"]},
                        time_horizon="short"
                    )
                    signals.append(sell_signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Market making strategy error: {e}")
            return []
    
    async def _find_illiquid_markets(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Find illiquid markets suitable for market making"""
        try:
            query = text("""
                SELECT 
                    st.team,
                    st.venue,
                    l.section,
                    AVG(l.price) as avg_price,
                    COUNT(*) as listing_count,
                    STDDEV(l.price) as price_stddev
                FROM listings l
                JOIN season_tickets st ON l.season_ticket_id = st.id
                WHERE l.status = 'active'
                  AND l.created_at >= date('now', '-7 days')
                GROUP BY st.team, st.venue, l.section
                HAVING COUNT(*) < 10  -- Low liquidity threshold
                ORDER BY listing_count ASC
                LIMIT 10
            """)
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            markets = []
            for row in rows:
                if row[3]:  # avg_price exists
                    liquidity_score = float(row[4]) / 100  # Normalize listing count
                    spread_estimate = (float(row[5]) if row[5] else 0.1) * 2  # 2x standard deviation
                    
                    markets.append({
                        "team": row[0],
                        "venue": row[1],
                        "section": row[2],
                        "estimated_fair_value": float(row[3]),
                        "liquidity_score": liquidity_score,
                        "estimated_spread": spread_estimate
                    })
            
            return markets
            
        except Exception as e:
            logger.error(f"Illiquid market detection error: {e}")
            return []


class PortfolioOptimizer(BaseStrategy):
    """Modern Portfolio Theory optimizer for ticket portfolios"""
    
    def __init__(self):
        super().__init__("PortfolioOptimization")
    
    async def generate_signals(
        self, 
        portfolio_data: Dict[str, Any], 
        market_analysis: Dict[str, Any], 
        db: AsyncSession
    ) -> List[TradeRecommendation]:
        """Generate portfolio optimization signals"""
        try:
            if not SCIPY_AVAILABLE:
                logger.warning("SciPy not available for portfolio optimization")
                return []
            
            # Get current portfolio composition
            current_positions = portfolio_data.get("positions", [])
            
            # Calculate expected returns and covariance matrix
            expected_returns, cov_matrix = await self._calculate_portfolio_metrics(current_positions, db)
            
            if expected_returns is None or cov_matrix is None:
                return []
            
            # Optimize portfolio allocation
            optimal_weights = await self._optimize_portfolio(expected_returns, cov_matrix)
            
            # Generate rebalancing signals
            signals = await self._generate_rebalancing_signals(
                current_positions, optimal_weights, portfolio_data
            )
            
            return signals
            
        except Exception as e:
            logger.error(f"Portfolio optimization error: {e}")
            return []
    
    async def _calculate_portfolio_metrics(
        self, 
        positions: List[Dict[str, Any]], 
        db: AsyncSession
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Calculate expected returns and covariance matrix"""
        try:
            if not positions:
                return None, None
            
            # Simplified calculation - in practice would use historical returns
            n_assets = len(positions)
            
            # Mock expected returns (would be calculated from historical data)
            expected_returns = np.random.normal(0.05, 0.02, n_assets)  # 5% expected return
            
            # Mock covariance matrix (would be calculated from historical correlations)
            correlations = np.random.uniform(0.1, 0.6, (n_assets, n_assets))
            np.fill_diagonal(correlations, 1.0)
            
            volatilities = np.random.uniform(0.15, 0.35, n_assets)  # 15-35% volatility
            cov_matrix = np.outer(volatilities, volatilities) * correlations
            
            return expected_returns, cov_matrix
            
        except Exception as e:
            logger.error(f"Portfolio metrics calculation error: {e}")
            return None, None
    
    async def _optimize_portfolio(
        self, 
        expected_returns: np.ndarray, 
        cov_matrix: np.ndarray
    ) -> np.ndarray:
        """Optimize portfolio using mean-variance optimization"""
        try:
            n_assets = len(expected_returns)
            
            # Objective function: maximize Sharpe ratio
            def neg_sharpe_ratio(weights):
                portfolio_return = np.sum(expected_returns * weights)
                portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                return -(portfolio_return - 0.02) / portfolio_volatility  # Assuming 2% risk-free rate
            
            # Constraints
            constraints = [
                {"type": "eq", "fun": lambda x: np.sum(x) - 1},  # Weights sum to 1
            ]
            
            # Bounds (0 to 50% per asset)
            bounds = [(0, 0.5) for _ in range(n_assets)]
            
            # Initial guess (equal weights)
            x0 = np.array([1.0 / n_assets] * n_assets)
            
            # Optimize
            result = sco.minimize(
                neg_sharpe_ratio,
                x0,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints
            )
            
            if result.success:
                return result.x
            else:
                logger.warning("Portfolio optimization failed, using equal weights")
                return x0
            
        except Exception as e:
            logger.error(f"Portfolio optimization error: {e}")
            return np.array([1.0 / len(expected_returns)] * len(expected_returns))
    
    async def _generate_rebalancing_signals(
        self, 
        current_positions: List[Dict[str, Any]], 
        optimal_weights: np.ndarray, 
        portfolio_data: Dict[str, Any]
    ) -> List[TradeRecommendation]:
        """Generate signals to rebalance portfolio to optimal weights"""
        try:
            signals = []
            total_value = portfolio_data.get("total_value", 0)
            
            if total_value == 0:
                return signals
            
            for i, position in enumerate(current_positions):
                if i >= len(optimal_weights):
                    continue
                
                current_weight = position.get("value", 0) / total_value
                target_weight = optimal_weights[i]
                weight_diff = target_weight - current_weight
                
                # Only rebalance if difference is significant (> 5%)
                if abs(weight_diff) > 0.05:
                    if weight_diff > 0:  # Need to buy more
                        signal = TradeRecommendation(
                            signal=TradeSignal.BUY,
                            confidence=min(abs(weight_diff) * 10, 1.0),
                            target_price=position.get("current_price", 0),
                            stop_loss=None,
                            take_profit=None,
                            position_size=abs(weight_diff),
                            reasoning=f"Portfolio rebalancing: increase weight by {weight_diff:.1%}",
                            risk_metrics={"weight_diff": weight_diff, "target_weight": target_weight},
                            time_horizon="medium"
                        )
                        signals.append(signal)
                    else:  # Need to sell
                        signal = TradeRecommendation(
                            signal=TradeSignal.SELL,
                            confidence=min(abs(weight_diff) * 10, 1.0),
                            target_price=position.get("current_price", 0),
                            stop_loss=None,
                            take_profit=None,
                            position_size=abs(weight_diff),
                            reasoning=f"Portfolio rebalancing: decrease weight by {abs(weight_diff):.1%}",
                            risk_metrics={"weight_diff": weight_diff, "target_weight": target_weight},
                            time_horizon="medium"
                        )
                        signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Rebalancing signals generation error: {e}")
            return []


class AdvancedRiskManagement:
    """Comprehensive risk management framework"""
    
    def __init__(self):
        self.risk_models = {
            'market_risk': MarketRiskModel(),
            'liquidity_risk': LiquidityRiskModel(),
            'operational_risk': OperationalRiskModel(),
            'concentration_risk': ConcentrationRiskModel()
        }
    
    async def adjust_position_sizes(
        self, 
        signals: List[TradeRecommendation], 
        portfolio_data: Dict[str, Any], 
        db: AsyncSession
    ) -> List[TradeRecommendation]:
        """Adjust position sizes based on comprehensive risk assessment"""
        try:
            # Assess overall portfolio risk
            portfolio_risk = await self._assess_portfolio_risk(portfolio_data, db)
            
            adjusted_signals = []
            
            for signal in signals:
                # Calculate individual trade risk
                trade_risk = await self._calculate_trade_risk(signal, portfolio_data, db)
                
                # Adjust position size based on risk
                risk_adjusted_size = self._apply_risk_adjustments(
                    signal.position_size, 
                    trade_risk, 
                    portfolio_risk
                )
                
                # Create adjusted signal
                adjusted_signal = TradeRecommendation(
                    signal=signal.signal,
                    confidence=signal.confidence,
                    target_price=signal.target_price,
                    stop_loss=signal.stop_loss,
                    take_profit=signal.take_profit,
                    position_size=risk_adjusted_size,
                    reasoning=f"{signal.reasoning} (Risk-adjusted)",
                    risk_metrics={
                        **signal.risk_metrics,
                        "trade_risk": trade_risk,
                        "portfolio_risk": portfolio_risk,
                        "original_size": signal.position_size,
                        "risk_adjustment": risk_adjusted_size / signal.position_size
                    },
                    time_horizon=signal.time_horizon
                )
                
                adjusted_signals.append(adjusted_signal)
            
            return adjusted_signals
            
        except Exception as e:
            logger.error(f"Risk adjustment error: {e}")
            return signals  # Return original signals if risk adjustment fails
    
    async def _assess_portfolio_risk(
        self, 
        portfolio_data: Dict[str, Any], 
        db: AsyncSession
    ) -> Dict[str, float]:
        """Multi-dimensional portfolio risk assessment"""
        try:
            risk_assessment = {}
            
            # Market risk
            risk_assessment["market_risk"] = await self.risk_models["market_risk"].assess(portfolio_data, db)
            
            # Liquidity risk
            risk_assessment["liquidity_risk"] = await self.risk_models["liquidity_risk"].assess(portfolio_data, db)
            
            # Operational risk
            risk_assessment["operational_risk"] = await self.risk_models["operational_risk"].assess(portfolio_data, db)
            
            # Concentration risk
            risk_assessment["concentration_risk"] = await self.risk_models["concentration_risk"].assess(portfolio_data, db)
            
            # Overall risk score
            risk_assessment["overall_risk"] = np.mean(list(risk_assessment.values()))
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Portfolio risk assessment error: {e}")
            return {"overall_risk": 0.5}  # Moderate risk default
    
    async def _calculate_trade_risk(
        self, 
        signal: TradeRecommendation, 
        portfolio_data: Dict[str, Any], 
        db: AsyncSession
    ) -> float:
        """Calculate risk score for individual trade"""
        try:
            risk_factors = []
            
            # Confidence-based risk
            risk_factors.append(1.0 - signal.confidence)
            
            # Position size risk
            risk_factors.append(min(signal.position_size * 10, 1.0))  # Large positions are riskier
            
            # Time horizon risk
            time_risk = {"immediate": 0.8, "short": 0.6, "medium": 0.4, "long": 0.2}
            risk_factors.append(time_risk.get(signal.time_horizon, 0.5))
            
            # Price volatility risk (from signal metrics)
            vol_risk = signal.risk_metrics.get("price_volatility", 0.5)
            risk_factors.append(vol_risk)
            
            return np.mean(risk_factors)
            
        except Exception as e:
            logger.error(f"Trade risk calculation error: {e}")
            return 0.5
    
    def _apply_risk_adjustments(
        self, 
        original_size: float, 
        trade_risk: float, 
        portfolio_risk: Dict[str, float]
    ) -> float:
        """Apply risk-based position size adjustments"""
        try:
            # Base adjustment factor
            risk_factor = 1.0
            
            # Adjust for trade-specific risk
            risk_factor *= (1.0 - trade_risk * 0.5)  # Reduce size for high-risk trades
            
            # Adjust for overall portfolio risk
            overall_risk = portfolio_risk.get("overall_risk", 0.5)
            risk_factor *= (1.0 - overall_risk * 0.3)  # Reduce size for high portfolio risk
            
            # Apply concentration limits
            concentration_risk = portfolio_risk.get("concentration_risk", 0.5)
            if concentration_risk > 0.7:
                risk_factor *= 0.5  # Halve position size for high concentration
            
            # Ensure minimum and maximum bounds
            adjusted_size = original_size * risk_factor
            return max(0.01, min(0.5, adjusted_size))  # Between 1% and 50%
            
        except Exception as e:
            logger.error(f"Risk adjustment application error: {e}")
            return original_size


# Risk model classes
class BaseRiskModel(ABC):
    """Base class for risk models"""
    
    @abstractmethod
    async def assess(self, portfolio_data: Dict[str, Any], db: AsyncSession) -> float:
        """Assess risk level (0-1 scale)"""
        pass


class MarketRiskModel(BaseRiskModel):
    """Market risk assessment model"""
    
    async def assess(self, portfolio_data: Dict[str, Any], db: AsyncSession) -> float:
        """Assess market risk level"""
        try:
            # Simplified market risk calculation
            # In practice, would calculate VaR, beta, etc.
            
            volatility = portfolio_data.get("volatility", 0.2)
            beta = portfolio_data.get("beta", 1.0)
            
            # Risk score based on volatility and market exposure
            risk_score = min(1.0, volatility * 2 + abs(beta - 1.0) * 0.5)
            
            return risk_score
            
        except Exception as e:
            logger.error(f"Market risk assessment error: {e}")
            return 0.5


class LiquidityRiskModel(BaseRiskModel):
    """Liquidity risk assessment model"""
    
    async def assess(self, portfolio_data: Dict[str, Any], db: AsyncSession) -> float:
        """Assess liquidity risk level"""
        try:
            # Calculate average time to liquidation
            positions = portfolio_data.get("positions", [])
            
            if not positions:
                return 0.0
            
            liquidity_scores = []
            
            for position in positions:
                # Mock liquidity calculation
                listing_count = position.get("market_listings", 10)
                avg_time_to_sale = position.get("avg_time_to_sale", 7)
                
                liquidity_score = min(1.0, avg_time_to_sale / 30 + (1 / max(listing_count, 1)) * 0.5)
                liquidity_scores.append(liquidity_score)
            
            return np.mean(liquidity_scores)
            
        except Exception as e:
            logger.error(f"Liquidity risk assessment error: {e}")
            return 0.5


class OperationalRiskModel(BaseRiskModel):
    """Operational risk assessment model"""
    
    async def assess(self, portfolio_data: Dict[str, Any], db: AsyncSession) -> float:
        """Assess operational risk level"""
        try:
            # Assess platform dependencies, execution risk, etc.
            
            platform_count = len(portfolio_data.get("platforms", []))
            execution_success_rate = portfolio_data.get("execution_success_rate", 0.95)
            
            # Risk score based on platform diversification and execution reliability
            platform_risk = max(0, 1.0 - platform_count / 4)  # Less risk with more platforms
            execution_risk = 1.0 - execution_success_rate
            
            return (platform_risk + execution_risk) / 2
            
        except Exception as e:
            logger.error(f"Operational risk assessment error: {e}")
            return 0.3


class ConcentrationRiskModel(BaseRiskModel):
    """Concentration risk assessment model"""
    
    async def assess(self, portfolio_data: Dict[str, Any], db: AsyncSession) -> float:
        """Assess concentration risk level"""
        try:
            positions = portfolio_data.get("positions", [])
            
            if not positions:
                return 0.0
            
            # Calculate Herfindahl-Hirschman Index for concentration
            total_value = portfolio_data.get("total_value", 0)
            
            if total_value == 0:
                return 0.0
            
            weights = [pos.get("value", 0) / total_value for pos in positions]
            hhi = sum(w**2 for w in weights)
            
            # Convert HHI to risk score (higher HHI = more concentration = higher risk)
            concentration_risk = min(1.0, hhi * 2)  # Scale HHI to 0-1
            
            return concentration_risk
            
        except Exception as e:
            logger.error(f"Concentration risk assessment error: {e}")
            return 0.5