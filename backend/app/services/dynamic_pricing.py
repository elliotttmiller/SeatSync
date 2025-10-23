"""
Dynamic Pricing Optimization Engine
State-of-the-Art Real-time Price Optimization

Based on research from:
- Mosaic Data Science predictive pricing strategies
- Dynamic pricing for sports events
- Revenue optimization algorithms
- A/B testing frameworks

Features:
- Real-time price optimization
- Revenue maximization algorithms
- Competitive pricing strategies
- Price elasticity-based optimization
- Constraint-based optimization
- A/B testing framework
- Multi-objective optimization
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import pandas as pd

try:
    from scipy.optimize import minimize, differential_evolution
    from scipy.stats import beta
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

logger = logging.getLogger(__name__)


class PricingStrategy(Enum):
    """Available pricing strategies"""
    REVENUE_MAXIMIZATION = "revenue_max"
    MARKET_SHARE = "market_share"
    COMPETITIVE = "competitive"
    VALUE_BASED = "value_based"
    TIME_BASED = "time_based"
    DEMAND_BASED = "demand_based"
    PSYCHOLOGICAL = "psychological"


@dataclass
class PriceConstraints:
    """Constraints for price optimization"""
    min_price: float
    max_price: float
    min_margin: float = 0.1  # 10% minimum margin
    max_discount: float = 0.5  # Maximum 50% discount
    price_step: float = 1.0  # Price must be multiple of this
    
    def validate_price(self, price: float) -> float:
        """Validate and adjust price to meet constraints"""
        # Apply bounds
        price = max(self.min_price, min(price, self.max_price))
        
        # Round to price step
        price = round(price / self.price_step) * self.price_step
        
        return price


@dataclass
class OptimalPrice:
    """Optimal price recommendation"""
    price: float
    expected_revenue: float
    expected_demand: float
    confidence: float
    strategy: str
    reasoning: List[str] = field(default_factory=list)
    alternative_prices: List[Dict[str, float]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'optimal_price': round(self.price, 2),
            'expected_revenue': round(self.expected_revenue, 2),
            'expected_demand': round(self.expected_demand, 2),
            'confidence': round(self.confidence, 3),
            'strategy': self.strategy,
            'reasoning': self.reasoning,
            'alternatives': [
                {k: round(v, 2) for k, v in alt.items()}
                for alt in self.alternative_prices
            ]
        }


class DemandFunction:
    """
    Demand function modeling
    Q = f(P, X) where Q is demand, P is price, X are other factors
    """
    
    def __init__(self, elasticity: float = -1.5, base_demand: float = 100):
        self.elasticity = elasticity
        self.base_demand = base_demand
        self.base_price = 100.0
        
    def estimate_demand(
        self,
        price: float,
        external_factors: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Estimate demand at given price
        
        Uses constant elasticity demand function:
        Q = Q0 * (P / P0)^elasticity * adjustment_factor
        """
        # Base demand from elasticity
        demand = self.base_demand * np.power(
            price / self.base_price,
            self.elasticity
        )
        
        # Adjust for external factors
        if external_factors:
            adjustment = 1.0
            
            # Team performance boost (0-1 scale)
            if 'team_performance' in external_factors:
                adjustment *= (1.0 + external_factors['team_performance'] * 0.2)
            
            # Time urgency (closer to event = higher demand)
            if 'days_until_event' in external_factors:
                days = external_factors['days_until_event']
                if days < 7:
                    adjustment *= 1.2  # 20% boost for last week
                elif days < 3:
                    adjustment *= 1.5  # 50% boost for last 3 days
            
            # Weather factor
            if 'weather_score' in external_factors:
                adjustment *= (0.8 + external_factors['weather_score'] * 0.4)
            
            # Competing events (negative impact)
            if 'competing_events' in external_factors:
                adjustment *= (1.0 - external_factors['competing_events'] * 0.1)
            
            demand *= adjustment
        
        return max(0, demand)
    
    def estimate_revenue(
        self,
        price: float,
        external_factors: Optional[Dict[str, float]] = None
    ) -> float:
        """Estimate revenue at given price"""
        demand = self.estimate_demand(price, external_factors)
        return price * demand


class RevenueOptimizer:
    """
    Revenue optimization engine
    Finds optimal price to maximize revenue
    """
    
    def __init__(
        self,
        demand_function: DemandFunction,
        constraints: PriceConstraints
    ):
        self.demand_function = demand_function
        self.constraints = constraints
        
    def optimize(
        self,
        external_factors: Optional[Dict[str, float]] = None,
        method: str = 'bounded'
    ) -> OptimalPrice:
        """
        Find optimal price to maximize revenue
        
        Args:
            external_factors: External demand factors
            method: 'bounded' or 'global' optimization
            
        Returns:
            OptimalPrice object
        """
        if not SCIPY_AVAILABLE:
            logger.warning("SciPy not available, using simple optimization")
            return self._simple_optimize(external_factors)
        
        # Objective function (negative revenue for minimization)
        def objective(price):
            revenue = self.demand_function.estimate_revenue(
                price[0],
                external_factors
            )
            return -revenue  # Negative for minimization
        
        # Bounds
        bounds = [(self.constraints.min_price, self.constraints.max_price)]
        
        try:
            if method == 'global':
                # Global optimization (slower but more thorough)
                result = differential_evolution(
                    objective,
                    bounds,
                    seed=42,
                    maxiter=100
                )
            else:
                # Local optimization (faster)
                x0 = [(self.constraints.min_price + self.constraints.max_price) / 2]
                result = minimize(
                    objective,
                    x0,
                    method='L-BFGS-B',
                    bounds=bounds
                )
            
            optimal_price = self.constraints.validate_price(result.x[0])
            optimal_demand = self.demand_function.estimate_demand(
                optimal_price,
                external_factors
            )
            optimal_revenue = optimal_price * optimal_demand
            
            # Generate alternative prices
            alternatives = self._generate_alternatives(
                optimal_price,
                external_factors
            )
            
            return OptimalPrice(
                price=optimal_price,
                expected_revenue=optimal_revenue,
                expected_demand=optimal_demand,
                confidence=0.85,
                strategy=PricingStrategy.REVENUE_MAXIMIZATION.value,
                reasoning=[
                    f"Optimal price balances demand ({optimal_demand:.1f}) and price",
                    f"Expected revenue: ${optimal_revenue:.2f}",
                    "Based on price elasticity and market conditions"
                ],
                alternative_prices=alternatives
            )
            
        except Exception as e:
            logger.error(f"Revenue optimization error: {e}")
            return self._simple_optimize(external_factors)
    
    def _simple_optimize(
        self,
        external_factors: Optional[Dict[str, float]] = None
    ) -> OptimalPrice:
        """Simple grid search optimization (fallback)"""
        # Test prices in increments
        prices = np.arange(
            self.constraints.min_price,
            self.constraints.max_price,
            self.constraints.price_step
        )
        
        best_revenue = 0
        best_price = self.constraints.min_price
        best_demand = 0
        
        for price in prices:
            demand = self.demand_function.estimate_demand(price, external_factors)
            revenue = price * demand
            
            if revenue > best_revenue:
                best_revenue = revenue
                best_price = price
                best_demand = demand
        
        return OptimalPrice(
            price=best_price,
            expected_revenue=best_revenue,
            expected_demand=best_demand,
            confidence=0.7,
            strategy=PricingStrategy.REVENUE_MAXIMIZATION.value,
            reasoning=["Simple grid search optimization"],
            alternative_prices=[]
        )
    
    def _generate_alternatives(
        self,
        optimal_price: float,
        external_factors: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, float]]:
        """Generate alternative pricing options"""
        alternatives = []
        
        # Lower price option (higher volume)
        lower_price = optimal_price * 0.9
        lower_demand = self.demand_function.estimate_demand(
            lower_price,
            external_factors
        )
        alternatives.append({
            'price': lower_price,
            'demand': lower_demand,
            'revenue': lower_price * lower_demand,
            'label': 'Volume-focused'
        })
        
        # Higher price option (higher margin)
        higher_price = optimal_price * 1.1
        higher_demand = self.demand_function.estimate_demand(
            higher_price,
            external_factors
        )
        alternatives.append({
            'price': higher_price,
            'demand': higher_demand,
            'revenue': higher_price * higher_demand,
            'label': 'Margin-focused'
        })
        
        return alternatives


class CompetitivePricingStrategy:
    """
    Competitive pricing strategy
    Price relative to competitors
    """
    
    def __init__(self, target_position: str = 'match'):
        """
        Args:
            target_position: 'undercut', 'match', or 'premium'
        """
        self.target_position = target_position
        
    def calculate_price(
        self,
        competitor_prices: List[float],
        constraints: PriceConstraints
    ) -> OptimalPrice:
        """
        Calculate competitive price
        
        Args:
            competitor_prices: List of competitor prices
            constraints: Price constraints
        """
        if not competitor_prices:
            # No competitors, use middle of range
            price = (constraints.min_price + constraints.max_price) / 2
            reasoning = ["No competitor data available"]
        else:
            avg_competitor_price = np.mean(competitor_prices)
            min_competitor_price = min(competitor_prices)
            
            if self.target_position == 'undercut':
                # Price 5% below lowest competitor
                price = min_competitor_price * 0.95
                reasoning = [
                    f"Undercut lowest competitor (${min_competitor_price:.2f})",
                    "Aggressive market share strategy"
                ]
            elif self.target_position == 'premium':
                # Price 10% above average
                price = avg_competitor_price * 1.10
                reasoning = [
                    f"Premium positioning above market avg (${avg_competitor_price:.2f})",
                    "Value-based pricing strategy"
                ]
            else:  # match
                # Match average competitor price
                price = avg_competitor_price
                reasoning = [
                    f"Match average competitor price (${avg_competitor_price:.2f})",
                    "Market-neutral positioning"
                ]
        
        price = constraints.validate_price(price)
        
        return OptimalPrice(
            price=price,
            expected_revenue=0.0,  # Would need demand model
            expected_demand=0.0,
            confidence=0.75,
            strategy=PricingStrategy.COMPETITIVE.value,
            reasoning=reasoning
        )


class TimeBasedPricingStrategy:
    """
    Time-based pricing strategy
    Adjust prices based on time until event
    """
    
    def __init__(self):
        # Pricing multipliers by days until event
        self.time_multipliers = {
            90: 0.85,   # Early bird (15% discount)
            60: 0.90,   # 60 days out (10% discount)
            30: 1.00,   # 30 days (base price)
            14: 1.05,   # 2 weeks (5% premium)
            7: 1.15,    # 1 week (15% premium)
            3: 1.25,    # 3 days (25% premium)
            1: 1.40     # Last day (40% premium)
        }
    
    def calculate_price(
        self,
        base_price: float,
        days_until_event: int,
        constraints: PriceConstraints
    ) -> OptimalPrice:
        """
        Calculate time-based price
        
        Args:
            base_price: Base/reference price
            days_until_event: Days until event
            constraints: Price constraints
        """
        # Find appropriate multiplier
        multiplier = 1.0
        reasoning = []
        
        for days_threshold, mult in sorted(self.time_multipliers.items()):
            if days_until_event >= days_threshold:
                multiplier = mult
                reasoning.append(
                    f"{days_threshold}+ days out: {mult:.0%} of base"
                )
                break
        
        price = base_price * multiplier
        price = constraints.validate_price(price)
        
        if multiplier < 1.0:
            reasoning.append("Early bird discount applied")
        elif multiplier > 1.0:
            reasoning.append("Urgency premium applied")
        
        return OptimalPrice(
            price=price,
            expected_revenue=0.0,
            expected_demand=0.0,
            confidence=0.8,
            strategy=PricingStrategy.TIME_BASED.value,
            reasoning=reasoning
        )


class PsychologicalPricingStrategy:
    """
    Psychological pricing (charm pricing)
    Use prices ending in .99, .95, etc.
    """
    
    def __init__(self, pricing_type: str = 'charm'):
        """
        Args:
            pricing_type: 'charm' (.99), 'prestige' (round), or 'value' (.95)
        """
        self.pricing_type = pricing_type
        
    def adjust_price(self, price: float) -> float:
        """Apply psychological pricing adjustment"""
        if self.pricing_type == 'charm':
            # Round up to next dollar, then subtract 0.01
            return np.ceil(price) - 0.01
        elif self.pricing_type == 'prestige':
            # Round to nearest $5 or $10
            if price >= 100:
                return round(price / 10) * 10
            else:
                return round(price / 5) * 5
        elif self.pricing_type == 'value':
            # End in .95
            return np.floor(price) + 0.95
        else:
            return price


class ABTestingFramework:
    """
    A/B testing framework for pricing experiments
    Uses Thompson sampling (Bayesian approach)
    """
    
    def __init__(self):
        self.experiments = {}
        
    def create_experiment(
        self,
        experiment_id: str,
        control_price: float,
        test_prices: List[float]
    ):
        """
        Create a new A/B test
        
        Args:
            experiment_id: Unique experiment identifier
            control_price: Control (baseline) price
            test_prices: List of test prices to compare
        """
        self.experiments[experiment_id] = {
            'prices': [control_price] + test_prices,
            'successes': [1] * (len(test_prices) + 1),  # Prior successes
            'failures': [1] * (len(test_prices) + 1),   # Prior failures
            'created_at': datetime.utcnow()
        }
        
        logger.info(f"Created experiment {experiment_id} with {len(test_prices)} variants")
    
    def select_price(self, experiment_id: str) -> Optional[float]:
        """
        Select price using Thompson sampling
        
        Returns:
            Selected price for this trial
        """
        if experiment_id not in self.experiments:
            return None
        
        exp = self.experiments[experiment_id]
        
        # Sample from beta distribution for each variant
        samples = []
        for i in range(len(exp['prices'])):
            sample = beta.rvs(
                exp['successes'][i],
                exp['failures'][i]
            )
            samples.append(sample)
        
        # Select variant with highest sample
        best_idx = np.argmax(samples)
        return exp['prices'][best_idx]
    
    def record_outcome(
        self,
        experiment_id: str,
        price: float,
        success: bool
    ):
        """
        Record outcome of a trial
        
        Args:
            experiment_id: Experiment ID
            price: Price that was used
            success: True if sale was made, False otherwise
        """
        if experiment_id not in self.experiments:
            return
        
        exp = self.experiments[experiment_id]
        
        # Find price index
        try:
            price_idx = exp['prices'].index(price)
        except ValueError:
            logger.warning(f"Price {price} not found in experiment")
            return
        
        # Update counts
        if success:
            exp['successes'][price_idx] += 1
        else:
            exp['failures'][price_idx] += 1
    
    def get_results(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get experiment results and confidence"""
        if experiment_id not in self.experiments:
            return None
        
        exp = self.experiments[experiment_id]
        
        results = []
        for i, price in enumerate(exp['prices']):
            successes = exp['successes'][i]
            failures = exp['failures'][i]
            total = successes + failures - 2  # Subtract priors
            
            if total > 0:
                conversion_rate = (successes - 1) / total
            else:
                conversion_rate = 0.0
            
            results.append({
                'price': price,
                'trials': total,
                'conversions': successes - 1,
                'conversion_rate': conversion_rate,
                'is_control': i == 0
            })
        
        return {
            'experiment_id': experiment_id,
            'variants': results,
            'created_at': exp['created_at'].isoformat()
        }


class DynamicPricingEngine:
    """
    Comprehensive dynamic pricing engine
    Combines multiple strategies for optimal pricing
    """
    
    def __init__(self):
        self.revenue_optimizer = None
        self.competitive_strategy = CompetitivePricingStrategy()
        self.time_strategy = TimeBasedPricingStrategy()
        self.psychological_strategy = PsychologicalPricingStrategy()
        self.ab_testing = ABTestingFramework()
        
    def initialize(
        self,
        elasticity: float = -1.5,
        base_demand: float = 100
    ):
        """Initialize the pricing engine"""
        demand_function = DemandFunction(elasticity, base_demand)
        self.revenue_optimizer = RevenueOptimizer(
            demand_function,
            PriceConstraints(min_price=10, max_price=1000)
        )
        
        logger.info("Dynamic pricing engine initialized")
    
    async def calculate_optimal_price(
        self,
        strategy: PricingStrategy,
        base_price: float,
        external_factors: Optional[Dict[str, float]] = None,
        competitor_prices: Optional[List[float]] = None,
        days_until_event: Optional[int] = None,
        constraints: Optional[PriceConstraints] = None
    ) -> OptimalPrice:
        """
        Calculate optimal price using specified strategy
        
        Args:
            strategy: Pricing strategy to use
            base_price: Base/reference price
            external_factors: External demand factors
            competitor_prices: Competitor prices
            days_until_event: Days until event
            constraints: Price constraints
        """
        if constraints is None:
            constraints = PriceConstraints(
                min_price=base_price * 0.5,
                max_price=base_price * 2.0
            )
        
        try:
            if strategy == PricingStrategy.REVENUE_MAXIMIZATION:
                if self.revenue_optimizer:
                    result = self.revenue_optimizer.optimize(external_factors)
                else:
                    raise ValueError("Revenue optimizer not initialized")
                    
            elif strategy == PricingStrategy.COMPETITIVE:
                if not competitor_prices:
                    raise ValueError("Competitor prices required for competitive strategy")
                result = self.competitive_strategy.calculate_price(
                    competitor_prices,
                    constraints
                )
                
            elif strategy == PricingStrategy.TIME_BASED:
                if days_until_event is None:
                    raise ValueError("Days until event required for time-based strategy")
                result = self.time_strategy.calculate_price(
                    base_price,
                    days_until_event,
                    constraints
                )
                
            else:
                # Default to simple pricing
                result = OptimalPrice(
                    price=base_price,
                    expected_revenue=0.0,
                    expected_demand=0.0,
                    confidence=0.5,
                    strategy=strategy.value,
                    reasoning=["Default pricing - strategy not implemented"]
                )
            
            # Apply psychological pricing
            result.price = self.psychological_strategy.adjust_price(result.price)
            result.price = constraints.validate_price(result.price)
            
            return result
            
        except Exception as e:
            logger.error(f"Price calculation error: {e}")
            # Return fallback price
            return OptimalPrice(
                price=base_price,
                expected_revenue=0.0,
                expected_demand=0.0,
                confidence=0.3,
                strategy="fallback",
                reasoning=[f"Error occurred: {str(e)}"]
            )
    
    def start_ab_test(
        self,
        experiment_id: str,
        control_price: float,
        test_prices: List[float]
    ):
        """Start an A/B test"""
        self.ab_testing.create_experiment(experiment_id, control_price, test_prices)
    
    def get_ab_test_price(self, experiment_id: str) -> Optional[float]:
        """Get price for A/B test"""
        return self.ab_testing.select_price(experiment_id)
    
    def record_ab_test_outcome(
        self,
        experiment_id: str,
        price: float,
        success: bool
    ):
        """Record A/B test outcome"""
        self.ab_testing.record_outcome(experiment_id, price, success)
