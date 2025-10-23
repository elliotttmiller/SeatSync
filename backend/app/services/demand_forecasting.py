"""
Advanced Demand Forecasting
State-of-the-Art Time Series Prediction for Ticket Demand

Based on research from:
- Dynamic pricing for sports events (useR Conference)
- Facebook Prophet for time series forecasting
- ARIMA and seasonal decomposition methods
- CS109 demand curve analysis

Features:
- Prophet-based forecasting with seasonality
- ARIMA for classical time series analysis
- Exponential smoothing (Holt-Winters)
- Demand curve estimation
- Booking velocity tracking
- Sellout probability prediction
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logging.warning("Prophet not available. Install with: pip install prophet")

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from statsmodels.tsa.seasonal import seasonal_decompose
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class DemandForecast:
    """Demand forecast with confidence intervals"""
    timestamp: datetime
    predicted_demand: float
    lower_bound: float
    upper_bound: float
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'predicted_demand': round(self.predicted_demand, 2),
            'lower_bound': round(self.lower_bound, 2),
            'upper_bound': round(self.upper_bound, 2),
            'confidence': round(self.confidence, 3)
        }


@dataclass
class DemandCurve:
    """Demand curve at different price points"""
    price_points: List[float]
    demand_estimates: List[float]
    elasticity: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'price_points': [round(p, 2) for p in self.price_points],
            'demand_estimates': [round(d, 2) for d in self.demand_estimates],
            'elasticity': round(self.elasticity, 3)
        }


class ProphetDemandForecaster:
    """
    Facebook Prophet-based demand forecasting
    Handles seasonality, holidays, and special events automatically
    """
    
    def __init__(self):
        self.model = None
        self.is_fitted = False
        
    def fit(
        self,
        historical_data: pd.DataFrame,
        daily_seasonality: bool = True,
        weekly_seasonality: bool = True,
        yearly_seasonality: bool = False
    ):
        """
        Fit Prophet model on historical demand data
        
        Args:
            historical_data: DataFrame with 'ds' (date) and 'y' (demand) columns
            daily_seasonality: Include daily patterns
            weekly_seasonality: Include weekly patterns
            yearly_seasonality: Include yearly patterns
        """
        if not PROPHET_AVAILABLE:
            logger.error("Prophet not available")
            return False
        
        try:
            # Initialize model
            self.model = Prophet(
                growth='logistic',  # Bounded growth (can't exceed venue capacity)
                daily_seasonality=daily_seasonality,
                weekly_seasonality=weekly_seasonality,
                yearly_seasonality=yearly_seasonality,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0,
                holidays_prior_scale=10.0,
                seasonality_mode='multiplicative'
            )
            
            # Add custom seasonalities
            self.model.add_seasonality(
                name='monthly',
                period=30.5,
                fourier_order=5
            )
            
            # Add US holidays
            self.model.add_country_holidays(country_name='US')
            
            # Ensure data has capacity column for logistic growth
            if 'cap' not in historical_data.columns:
                # Estimate capacity as 1.2x max observed demand
                historical_data['cap'] = historical_data['y'].max() * 1.2
            
            if 'floor' not in historical_data.columns:
                historical_data['floor'] = 0
            
            # Fit model
            self.model.fit(historical_data)
            self.is_fitted = True
            
            logger.info("Prophet model fitted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Prophet fitting error: {e}")
            return False
    
    def forecast(
        self,
        periods: int,
        freq: str = 'D',
        capacity: Optional[float] = None
    ) -> List[DemandForecast]:
        """
        Forecast demand for future periods
        
        Args:
            periods: Number of periods to forecast
            freq: Frequency ('D' for daily, 'H' for hourly)
            capacity: Capacity constraint for logistic growth
            
        Returns:
            List of DemandForecast objects
        """
        if not self.is_fitted:
            logger.error("Model not fitted")
            return []
        
        try:
            # Create future dataframe
            future = self.model.make_future_dataframe(periods=periods, freq=freq)
            
            # Add capacity if provided
            if capacity:
                future['cap'] = capacity
                future['floor'] = 0
            
            # Make forecast
            forecast = self.model.predict(future)
            
            # Convert to DemandForecast objects (only future periods)
            results = []
            for idx in range(-periods, 0):
                row = forecast.iloc[idx]
                results.append(DemandForecast(
                    timestamp=row['ds'],
                    predicted_demand=max(0, row['yhat']),
                    lower_bound=max(0, row['yhat_lower']),
                    upper_bound=row['yhat_upper'],
                    confidence=0.8  # 80% confidence interval by default
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Prophet forecasting error: {e}")
            return []
    
    def get_components(self) -> Optional[pd.DataFrame]:
        """Get decomposed time series components (trend, seasonality)"""
        if not self.is_fitted:
            return None
        
        try:
            future = self.model.make_future_dataframe(periods=0)
            forecast = self.model.predict(future)
            return self.model.plot_components(forecast)
        except Exception as e:
            logger.error(f"Component extraction error: {e}")
            return None


class ARIMADemandForecaster:
    """
    Classical ARIMA-based demand forecasting
    Good for stationary time series with clear patterns
    """
    
    def __init__(self, order: Tuple[int, int, int] = (2, 1, 2)):
        """
        Initialize ARIMA forecaster
        
        Args:
            order: (p, d, q) where:
                p: AR order (autoregressive)
                d: Integration order (differencing)
                q: MA order (moving average)
        """
        self.model = None
        self.order = order
        self.is_fitted = False
        
    def fit(self, historical_data: pd.Series):
        """
        Fit ARIMA model on historical demand data
        
        Args:
            historical_data: Time series of historical demand
        """
        if not STATSMODELS_AVAILABLE:
            logger.error("statsmodels not available")
            return False
        
        try:
            # Fit ARIMA model
            self.model = ARIMA(historical_data, order=self.order)
            self.model = self.model.fit()
            self.is_fitted = True
            
            logger.info(f"ARIMA{self.order} model fitted successfully")
            logger.info(f"AIC: {self.model.aic:.2f}, BIC: {self.model.bic:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"ARIMA fitting error: {e}")
            return False
    
    def forecast(self, periods: int) -> List[DemandForecast]:
        """
        Forecast demand for future periods
        
        Args:
            periods: Number of periods to forecast
            
        Returns:
            List of DemandForecast objects
        """
        if not self.is_fitted:
            logger.error("Model not fitted")
            return []
        
        try:
            # Make forecast
            forecast_result = self.model.forecast(steps=periods)
            
            # Get confidence intervals
            forecast_ci = self.model.get_forecast(steps=periods).conf_int()
            
            # Convert to DemandForecast objects
            results = []
            base_date = datetime.utcnow()
            
            for i in range(periods):
                results.append(DemandForecast(
                    timestamp=base_date + timedelta(days=i+1),
                    predicted_demand=max(0, forecast_result[i]),
                    lower_bound=max(0, forecast_ci.iloc[i, 0]),
                    upper_bound=forecast_ci.iloc[i, 1],
                    confidence=0.95  # 95% confidence interval
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"ARIMA forecasting error: {e}")
            return []


class ExponentialSmoothingForecaster:
    """
    Holt-Winters exponential smoothing for demand forecasting
    Good for data with trend and seasonality
    """
    
    def __init__(
        self,
        seasonal_periods: int = 7,
        trend: str = 'add',
        seasonal: str = 'add'
    ):
        """
        Initialize exponential smoothing forecaster
        
        Args:
            seasonal_periods: Length of season (e.g., 7 for weekly)
            trend: 'add' or 'mul' for additive/multiplicative trend
            seasonal: 'add' or 'mul' for additive/multiplicative seasonality
        """
        self.model = None
        self.seasonal_periods = seasonal_periods
        self.trend = trend
        self.seasonal = seasonal
        self.is_fitted = False
        
    def fit(self, historical_data: pd.Series):
        """Fit exponential smoothing model"""
        if not STATSMODELS_AVAILABLE:
            logger.error("statsmodels not available")
            return False
        
        try:
            self.model = ExponentialSmoothing(
                historical_data,
                seasonal_periods=self.seasonal_periods,
                trend=self.trend,
                seasonal=self.seasonal
            )
            self.model = self.model.fit()
            self.is_fitted = True
            
            logger.info("Exponential smoothing model fitted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Exponential smoothing fitting error: {e}")
            return False
    
    def forecast(self, periods: int) -> List[DemandForecast]:
        """Forecast demand for future periods"""
        if not self.is_fitted:
            logger.error("Model not fitted")
            return []
        
        try:
            # Make forecast
            forecast_result = self.model.forecast(steps=periods)
            
            # Simple confidence intervals (no built-in method)
            # Use ±20% as rough estimate
            results = []
            base_date = datetime.utcnow()
            
            for i in range(periods):
                demand = max(0, forecast_result[i])
                margin = demand * 0.2
                
                results.append(DemandForecast(
                    timestamp=base_date + timedelta(days=i+1),
                    predicted_demand=demand,
                    lower_bound=max(0, demand - margin),
                    upper_bound=demand + margin,
                    confidence=0.8
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Exponential smoothing forecasting error: {e}")
            return []


class DemandCurveEstimator:
    """
    Estimate demand curves at different price points
    Critical for dynamic pricing optimization
    """
    
    def __init__(self):
        self.baseline_demand = None
        self.elasticity = -1.5  # Default price elasticity
        
    def estimate_from_historical(
        self,
        price_demand_data: pd.DataFrame
    ) -> Optional[DemandCurve]:
        """
        Estimate demand curve from historical price-demand pairs
        
        Args:
            price_demand_data: DataFrame with 'price' and 'demand' columns
            
        Returns:
            DemandCurve object
        """
        try:
            # Calculate log-log regression for elasticity
            log_price = np.log(price_demand_data['price'])
            log_demand = np.log(price_demand_data['demand'])
            
            # Simple linear regression
            coeffs = np.polyfit(log_price, log_demand, 1)
            self.elasticity = coeffs[0]
            
            # Get baseline demand at median price
            median_price = price_demand_data['price'].median()
            median_demand = price_demand_data['demand'].median()
            self.baseline_demand = median_demand
            
            logger.info(f"Estimated elasticity: {self.elasticity:.3f}")
            
            # Generate demand curve
            price_points = np.linspace(
                price_demand_data['price'].min(),
                price_demand_data['price'].max(),
                20
            )
            
            demand_estimates = self.predict_demand_at_prices(price_points)
            
            return DemandCurve(
                price_points=price_points.tolist(),
                demand_estimates=demand_estimates.tolist(),
                elasticity=self.elasticity
            )
            
        except Exception as e:
            logger.error(f"Demand curve estimation error: {e}")
            return None
    
    def predict_demand_at_prices(
        self,
        prices: np.ndarray
    ) -> np.ndarray:
        """
        Predict demand at given price points using elasticity
        
        Q = Q0 * (P / P0)^elasticity
        """
        if self.baseline_demand is None:
            logger.warning("No baseline demand set, using default")
            self.baseline_demand = 100
        
        # Baseline price (assumed to be $100)
        baseline_price = 100.0
        
        # Calculate demand at each price
        demand = self.baseline_demand * np.power(
            prices / baseline_price,
            self.elasticity
        )
        
        return np.maximum(demand, 0)  # Demand can't be negative


class BookingVelocityTracker:
    """
    Track booking velocity (rate of ticket sales over time)
    Critical indicator for dynamic pricing
    """
    
    def __init__(self):
        self.booking_history = []
        
    def add_booking(self, timestamp: datetime, quantity: int = 1):
        """Record a booking"""
        self.booking_history.append({
            'timestamp': timestamp,
            'quantity': quantity
        })
    
    def get_velocity(
        self,
        window_hours: int = 24
    ) -> float:
        """
        Calculate booking velocity (bookings per hour)
        
        Args:
            window_hours: Time window to calculate velocity
            
        Returns:
            Bookings per hour
        """
        if not self.booking_history:
            return 0.0
        
        # Filter to recent bookings
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)
        recent_bookings = [
            b for b in self.booking_history
            if b['timestamp'] > cutoff
        ]
        
        if not recent_bookings:
            return 0.0
        
        total_quantity = sum(b['quantity'] for b in recent_bookings)
        return total_quantity / window_hours
    
    def get_acceleration(
        self,
        short_window: int = 6,
        long_window: int = 24
    ) -> float:
        """
        Calculate booking acceleration (change in velocity)
        
        Returns:
            Positive = accelerating, Negative = decelerating
        """
        short_velocity = self.get_velocity(short_window)
        long_velocity = self.get_velocity(long_window)
        
        if long_velocity == 0:
            return 0.0
        
        return (short_velocity - long_velocity) / long_velocity
    
    def predict_sellout_time(
        self,
        remaining_inventory: int,
        window_hours: int = 24
    ) -> Optional[datetime]:
        """
        Predict when tickets will sell out based on current velocity
        
        Returns:
            Estimated sellout timestamp, or None if velocity is zero
        """
        velocity = self.get_velocity(window_hours)
        
        if velocity <= 0:
            return None
        
        hours_to_sellout = remaining_inventory / velocity
        sellout_time = datetime.utcnow() + timedelta(hours=hours_to_sellout)
        
        return sellout_time


class SelloutProbabilityPredictor:
    """
    Predict probability that event will sell out
    Uses logistic regression on historical features
    """
    
    def __init__(self):
        self.model = None
        
    def predict_sellout_probability(
        self,
        days_until_event: int,
        current_capacity_used: float,
        booking_velocity: float,
        price_vs_market: float,
        team_performance: float
    ) -> float:
        """
        Predict sellout probability based on multiple factors
        
        Args:
            days_until_event: Days remaining until event
            current_capacity_used: Percentage of capacity sold (0-1)
            booking_velocity: Current bookings per hour
            price_vs_market: Price relative to market average
            team_performance: Team win rate or performance score
            
        Returns:
            Probability of sellout (0-1)
        """
        # Simplified logistic model (in production, train on historical data)
        
        # Key factors:
        # - High capacity used = higher sellout probability
        # - High velocity = higher sellout probability
        # - Less time = higher sellout probability
        # - Lower price vs market = higher sellout probability
        # - Better team = higher sellout probability
        
        score = 0.0
        
        # Capacity factor (most important)
        score += current_capacity_used * 40
        
        # Time factor
        time_factor = 1.0 / max(days_until_event, 1)
        score += time_factor * 20
        
        # Velocity factor
        velocity_score = min(booking_velocity / 10.0, 1.0)  # Normalize
        score += velocity_score * 20
        
        # Price factor (inverse relationship)
        price_factor = max(0, 2.0 - price_vs_market)
        score += price_factor * 10
        
        # Team factor
        score += team_performance * 10
        
        # Apply sigmoid function
        probability = 1.0 / (1.0 + np.exp(-0.1 * (score - 50)))
        
        return min(max(probability, 0.0), 1.0)


class AdvancedDemandForecaster:
    """
    Comprehensive demand forecasting system
    Combines multiple methods for robust predictions
    """
    
    def __init__(self):
        self.prophet_forecaster = ProphetDemandForecaster()
        self.arima_forecaster = ARIMADemandForecaster()
        self.exp_smoothing_forecaster = ExponentialSmoothingForecaster()
        self.demand_curve_estimator = DemandCurveEstimator()
        self.booking_velocity_tracker = BookingVelocityTracker()
        self.sellout_predictor = SelloutProbabilityPredictor()
        
    async def forecast_demand(
        self,
        historical_data: pd.DataFrame,
        periods: int,
        method: str = 'prophet'
    ) -> List[DemandForecast]:
        """
        Forecast demand using specified method
        
        Args:
            historical_data: Historical demand data
            periods: Number of periods to forecast
            method: 'prophet', 'arima', or 'exponential'
            
        Returns:
            List of demand forecasts
        """
        if method == 'prophet' and PROPHET_AVAILABLE:
            self.prophet_forecaster.fit(historical_data)
            return self.prophet_forecaster.forecast(periods)
        elif method == 'arima' and STATSMODELS_AVAILABLE:
            self.arima_forecaster.fit(historical_data['y'])
            return self.arima_forecaster.forecast(periods)
        elif method == 'exponential' and STATSMODELS_AVAILABLE:
            self.exp_smoothing_forecaster.fit(historical_data['y'])
            return self.exp_smoothing_forecaster.forecast(periods)
        else:
            logger.error(f"Method {method} not available")
            return []
    
    async def estimate_demand_curve(
        self,
        price_demand_data: pd.DataFrame
    ) -> Optional[DemandCurve]:
        """Estimate demand curve from historical data"""
        return self.demand_curve_estimator.estimate_from_historical(price_demand_data)
    
    def track_booking(self, timestamp: datetime, quantity: int = 1):
        """Record a booking for velocity tracking"""
        self.booking_velocity_tracker.add_booking(timestamp, quantity)
    
    def get_booking_velocity(self) -> float:
        """Get current booking velocity"""
        return self.booking_velocity_tracker.get_velocity()
    
    def predict_sellout_time(
        self,
        remaining_inventory: int
    ) -> Optional[datetime]:
        """Predict sellout time based on velocity"""
        return self.booking_velocity_tracker.predict_sellout_time(remaining_inventory)
