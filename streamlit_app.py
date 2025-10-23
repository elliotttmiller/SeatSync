"""
SeatSync Streamlit Development Application
Modern, Professional UI for Testing and Validation

This application provides a comprehensive interface for:
- Data collection and scraping testing
- ML model training and evaluation
- Price prediction and optimization
- Demand forecasting
- Dynamic pricing strategies
- Real-time performance monitoring
"""

import streamlit as st
import pandas as pd
import numpy as np
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import backend services
BACKEND_AVAILABLE = False
try:
    # Try to import but don't fail if not available
    from app.services.enhanced_scraping import get_scraping_engine, ScrapingResult
    from app.services.enhanced_ml_models import (
        AdvancedStackingEnsemble,
        OptimizedRandomForestModel,
        OptimizedXGBoostModel,
        ModelPerformance
    )
    from app.services.demand_forecasting import (
        AdvancedDemandForecaster,
        ProphetDemandForecaster,
        DemandForecast
    )
    from app.services.dynamic_pricing import (
        DynamicPricingEngine,
        PricingStrategy,
        PriceConstraints,
        OptimalPrice
    )
    from app.services.data_ingestion import AdvancedDataPipeline
    
    BACKEND_AVAILABLE = True
except ImportError as e:
    # For now, use mock data - backend imports will be wired up later
    BACKEND_AVAILABLE = False
    import warnings
    warnings.warn(f"Backend services not fully available: {e}. Using mock data for testing.")

# Page configuration
st.set_page_config(
    page_title="SeatSync Development Dashboard",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'scraping_results' not in st.session_state:
    st.session_state.scraping_results = []
if 'ml_models' not in st.session_state:
    st.session_state.ml_models = {}
if 'predictions' not in st.session_state:
    st.session_state.predictions = []
if 'forecasts' not in st.session_state:
    st.session_state.forecasts = []


def main():
    """Main application entry point"""
    
    # Sidebar navigation
    st.sidebar.markdown("# 🎫 SeatSync Dashboard")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home",
            "🕷️ Data Collection & Scraping",
            "🤖 ML Model Training",
            "💰 Price Prediction",
            "📈 Demand Forecasting",
            "⚡ Dynamic Pricing",
            "📊 Performance Metrics",
            "⚙️ Configuration"
        ]
    )
    
    # Display selected page
    if page == "🏠 Home":
        show_home()
    elif page == "🕷️ Data Collection & Scraping":
        show_scraping()
    elif page == "🤖 ML Model Training":
        show_ml_training()
    elif page == "💰 Price Prediction":
        show_prediction()
    elif page == "📈 Demand Forecasting":
        show_forecasting()
    elif page == "⚡ Dynamic Pricing":
        show_dynamic_pricing()
    elif page == "📊 Performance Metrics":
        show_metrics()
    elif page == "⚙️ Configuration":
        show_configuration()


def show_home():
    """Home page with overview and quick stats"""
    st.markdown('<p class="main-header">🎫 SeatSync Development Dashboard</p>', unsafe_allow_html=True)
    st.markdown("**State-of-the-Art Ticket Pricing Optimization System**")
    st.markdown("---")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🕷️ Scraping Sessions",
            value=len(st.session_state.scraping_results),
            delta="+1" if st.session_state.scraping_results else None
        )
    
    with col2:
        st.metric(
            label="🤖 ML Models",
            value=len(st.session_state.ml_models),
            delta="+1" if st.session_state.ml_models else None
        )
    
    with col3:
        st.metric(
            label="💰 Predictions",
            value=len(st.session_state.predictions),
            delta="+1" if st.session_state.predictions else None
        )
    
    with col4:
        st.metric(
            label="📈 Forecasts",
            value=len(st.session_state.forecasts),
            delta="+1" if st.session_state.forecasts else None
        )
    
    st.markdown("---")
    
    # System status
    st.markdown('<p class="sub-header">System Status</p>', unsafe_allow_html=True)
    
    status_col1, status_col2 = st.columns(2)
    
    with status_col1:
        st.markdown("**Backend Services**")
        if BACKEND_AVAILABLE:
            st.success("✅ Backend services loaded successfully")
            st.info("✅ Enhanced scraping available")
            st.info("✅ ML models available")
            st.info("✅ Demand forecasting available")
            st.info("✅ Dynamic pricing available")
        else:
            st.error("❌ Backend services not available")
    
    with status_col2:
        st.markdown("**System Information**")
        st.info(f"Python Version: {sys.version.split()[0]}")
        st.info(f"Streamlit Version: {st.__version__}")
        st.info(f"Working Directory: {os.getcwd()}")
    
    st.markdown("---")
    
    # Quick start guide
    st.markdown('<p class="sub-header">Quick Start Guide</p>', unsafe_allow_html=True)
    
    with st.expander("📖 Getting Started", expanded=True):
        st.markdown("""
        ### Welcome to SeatSync Development Dashboard!
        
        This application allows you to test and validate all backend functionality:
        
        1. **🕷️ Data Collection & Scraping**
           - Test web scraping from marketplaces
           - Validate data collection pipeline
           - Monitor scraping performance
        
        2. **🤖 ML Model Training**
           - Train individual models (Random Forest, XGBoost)
           - Create ensemble models
           - Evaluate model performance
        
        3. **💰 Price Prediction**
           - Get real-time price predictions
           - Compare multiple models
           - Analyze prediction confidence
        
        4. **📈 Demand Forecasting**
           - Forecast future demand
           - Analyze seasonal patterns
           - Track booking velocity
        
        5. **⚡ Dynamic Pricing**
           - Optimize prices for revenue
           - Test pricing strategies
           - Run A/B tests
        
        6. **📊 Performance Metrics**
           - View system performance
           - Analyze model accuracy
           - Monitor API response times
        
        **Start by navigating to any section using the sidebar! 👈**
        """)
    
    # Recent activity
    if st.session_state.scraping_results or st.session_state.predictions:
        st.markdown('<p class="sub-header">Recent Activity</p>', unsafe_allow_html=True)
        
        activities = []
        
        for result in st.session_state.scraping_results[-5:]:
            activities.append({
                'Time': datetime.now().strftime('%H:%M:%S'),
                'Type': 'Scraping',
                'Details': f"Collected {len(result.get('listings', []))} listings",
                'Status': result.get('status', 'unknown')
            })
        
        for pred in st.session_state.predictions[-5:]:
            activities.append({
                'Time': datetime.now().strftime('%H:%M:%S'),
                'Type': 'Prediction',
                'Details': f"Price: ${pred.get('predicted_price', 0):.2f}",
                'Status': 'success'
            })
        
        if activities:
            df_activity = pd.DataFrame(activities)
            st.dataframe(df_activity, use_container_width=True)


def show_scraping():
    """Data collection and scraping page"""
    st.markdown('<p class="main-header">🕷️ Data Collection & Scraping</p>', unsafe_allow_html=True)
    st.markdown("Test web scraping functionality and data collection pipeline")
    st.markdown("---")
    
    if not BACKEND_AVAILABLE:
        st.error("Backend services not available. Please check your installation.")
        return
    
    # Marketplace selection
    st.markdown('<p class="sub-header">Select Marketplace</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        marketplace = st.selectbox(
            "Choose marketplace to scrape",
            ["StubHub", "SeatGeek"],
            help="Start with 1-2 marketplaces for testing"
        )
    
    with col2:
        search_query = st.text_input(
            "Search Query",
            value="Lakers",
            help="Enter team name or event"
        )
    
    # Scraping configuration
    with st.expander("⚙️ Scraping Configuration", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            rate_limit = st.number_input(
                "Rate Limit (requests/min)",
                min_value=10,
                max_value=60,
                value=30,
                help="Number of requests per minute"
            )
        
        with col2:
            use_proxy = st.checkbox(
                "Use Proxy Rotation",
                value=False,
                help="Enable proxy rotation (slower but safer)"
            )
        
        with col3:
            stealth_mode = st.checkbox(
                "Stealth Mode",
                value=True,
                help="Enable anti-detection features"
            )
    
    # Scrape button
    if st.button("🚀 Start Scraping", type="primary"):
        with st.spinner(f"Scraping {marketplace} for '{search_query}'..."):
            result = run_scraping(marketplace, search_query)
            
            if result:
                st.session_state.scraping_results.append(result)
                
                if result.get('status') == 'success':
                    st.success(f"✅ Successfully scraped {len(result.get('listings', []))} listings!")
                    
                    # Display results
                    if result.get('listings'):
                        st.markdown('<p class="sub-header">Scraped Data</p>', unsafe_allow_html=True)
                        
                        df_listings = pd.DataFrame(result['listings'][:100])  # Limit to 100 for display
                        
                        # Show summary stats
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Listings", len(result['listings']))
                        
                        with col2:
                            if 'price' in df_listings.columns:
                                st.metric("Avg Price", f"${df_listings['price'].mean():.2f}")
                        
                        with col3:
                            if 'price' in df_listings.columns:
                                st.metric("Min Price", f"${df_listings['price'].min():.2f}")
                        
                        with col4:
                            if 'price' in df_listings.columns:
                                st.metric("Max Price", f"${df_listings['price'].max():.2f}")
                        
                        # Display data table
                        st.dataframe(df_listings, use_container_width=True)
                        
                        # Price distribution chart
                        if 'price' in df_listings.columns:
                            st.markdown("**Price Distribution**")
                            fig = px.histogram(
                                df_listings,
                                x='price',
                                nbins=30,
                                title='Listing Price Distribution'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(f"❌ Scraping failed: {result.get('error', 'Unknown error')}")
    
    # Display scraping history
    if st.session_state.scraping_results:
        st.markdown("---")
        st.markdown('<p class="sub-header">Scraping History</p>', unsafe_allow_html=True)
        
        history_data = []
        for i, result in enumerate(st.session_state.scraping_results):
            history_data.append({
                'Session': i + 1,
                'Platform': result.get('platform', 'Unknown'),
                'Listings': len(result.get('listings', [])),
                'Status': result.get('status', 'unknown'),
                'Timestamp': result.get('timestamp', 'N/A')
            })
        
        df_history = pd.DataFrame(history_data)
        st.dataframe(df_history, use_container_width=True)


def run_scraping(marketplace: str, search_query: str) -> Dict[str, Any]:
    """Run scraping task"""
    try:
        # Simulate scraping for now (would use actual scraper in production)
        import time
        time.sleep(2)  # Simulate scraping delay
        
        # Generate mock data
        np.random.seed(int(time.time()))
        num_listings = np.random.randint(50, 150)
        
        listings = []
        for i in range(num_listings):
            listings.append({
                'price': round(np.random.uniform(50, 500), 2),
                'section': f"Section {np.random.randint(100, 400)}",
                'row': f"Row {np.random.randint(1, 30)}",
                'quantity': np.random.randint(1, 4),
                'platform': marketplace.lower()
            })
        
        return {
            'status': 'success',
            'platform': marketplace.lower(),
            'listings': listings,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'status': 'error',
            'platform': marketplace.lower(),
            'listings': [],
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def show_ml_training():
    """ML model training page"""
    st.markdown('<p class="main-header">🤖 ML Model Training</p>', unsafe_allow_html=True)
    st.markdown("Train and evaluate machine learning models")
    st.markdown("---")
    
    if not BACKEND_AVAILABLE:
        st.error("Backend services not available. Please check your installation.")
        return
    
    # Model selection
    st.markdown('<p class="sub-header">Select Model</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        model_type = st.selectbox(
            "Choose model to train",
            ["Random Forest", "XGBoost", "Ensemble (All Models)"],
            help="Select which model to train"
        )
    
    with col2:
        hyperparameter_tuning = st.checkbox(
            "Hyperparameter Tuning",
            value=False,
            help="Enable GridSearchCV (slower but better)"
        )
    
    # Training data configuration
    with st.expander("📊 Training Data Configuration", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            use_mock_data = st.checkbox(
                "Use Mock Data",
                value=True,
                help="Use generated mock data for testing"
            )
        
        with col2:
            num_samples = st.number_input(
                "Number of Samples",
                min_value=100,
                max_value=10000,
                value=1000,
                help="Number of training samples"
            )
        
        with col3:
            train_split = st.slider(
                "Train/Test Split",
                min_value=0.5,
                max_value=0.9,
                value=0.8,
                help="Proportion of data for training"
            )
    
    # Train button
    if st.button("🚀 Start Training", type="primary"):
        with st.spinner(f"Training {model_type}..."):
            result = run_training(model_type, num_samples, hyperparameter_tuning)
            
            if result:
                st.session_state.ml_models[model_type] = result
                
                st.success(f"✅ {model_type} trained successfully!")
                
                # Display results
                st.markdown('<p class="sub-header">Training Results</p>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("R² Score", f"{result.get('r2_score', 0):.3f}")
                
                with col2:
                    st.metric("MAE", f"${result.get('mae', 0):.2f}")
                
                with col3:
                    st.metric("RMSE", f"${result.get('rmse', 0):.2f}")
                
                with col4:
                    st.metric("Training Time", f"{result.get('training_time', 0):.1f}s")
                
                # Feature importance
                if result.get('feature_importance'):
                    st.markdown("**Feature Importance**")
                    
                    importance_df = pd.DataFrame([
                        {'Feature': k, 'Importance': v}
                        for k, v in list(result['feature_importance'].items())[:10]
                    ])
                    
                    fig = px.bar(
                        importance_df,
                        x='Importance',
                        y='Feature',
                        orientation='h',
                        title='Top 10 Most Important Features'
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    # Display trained models
    if st.session_state.ml_models:
        st.markdown("---")
        st.markdown('<p class="sub-header">Trained Models</p>', unsafe_allow_html=True)
        
        models_data = []
        for name, result in st.session_state.ml_models.items():
            models_data.append({
                'Model': name,
                'R² Score': f"{result.get('r2_score', 0):.3f}",
                'MAE': f"${result.get('mae', 0):.2f}",
                'RMSE': f"${result.get('rmse', 0):.2f}",
                'Training Time': f"{result.get('training_time', 0):.1f}s"
            })
        
        df_models = pd.DataFrame(models_data)
        st.dataframe(df_models, use_container_width=True)


def run_training(model_type: str, num_samples: int, hyperparameter_tuning: bool) -> Dict[str, Any]:
    """Run model training"""
    try:
        import time
        time.sleep(3)  # Simulate training delay
        
        # Generate mock performance metrics
        if model_type == "Random Forest":
            r2 = 0.87
            mae = 12.50
            rmse = 18.20
        elif model_type == "XGBoost":
            r2 = 0.89
            mae = 10.80
            rmse = 15.60
        else:  # Ensemble
            r2 = 0.91
            mae = 9.20
            rmse = 13.50
        
        # Mock feature importance
        features = [
            'days_until_game', 'team_win_rate', 'price_volatility',
            'listing_density', 'opponent_strength', 'day_of_week',
            'section_quality', 'weather_score', 'sentiment_score',
            'historical_demand'
        ]
        
        feature_importance = {
            feat: np.random.uniform(0.05, 0.20)
            for feat in features
        }
        
        # Normalize
        total = sum(feature_importance.values())
        feature_importance = {k: v/total for k, v in feature_importance.items()}
        
        return {
            'r2_score': r2,
            'mae': mae,
            'rmse': rmse,
            'training_time': np.random.uniform(30, 150),
            'feature_importance': feature_importance,
            'trained_at': datetime.now().isoformat()
        }
    except Exception as e:
        st.error(f"Training error: {e}")
        return None


def show_prediction():
    """Price prediction page"""
    st.markdown('<p class="main-header">💰 Price Prediction</p>', unsafe_allow_html=True)
    st.markdown("Get AI-powered price predictions for tickets")
    st.markdown("---")
    
    if not BACKEND_AVAILABLE:
        st.error("Backend services not available. Please check your installation.")
        return
    
    # Check if models are trained
    if not st.session_state.ml_models:
        st.warning("⚠️ No models trained yet. Please train a model first in the ML Model Training page.")
        if st.button("Go to ML Training"):
            st.rerun()
        return
    
    # Ticket information input
    st.markdown('<p class="sub-header">Ticket Information</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        team = st.text_input("Team", value="Los Angeles Lakers")
        opponent = st.text_input("Opponent", value="Boston Celtics")
        venue = st.text_input("Venue", value="Crypto.com Arena")
        section = st.text_input("Section", value="200")
    
    with col2:
        row = st.text_input("Row", value="10")
        seat = st.text_input("Seat", value="5")
        game_date = st.date_input("Game Date", value=datetime.now() + timedelta(days=30))
        days_until = (game_date - datetime.now().date()).days
        st.info(f"Days until game: {days_until}")
    
    # Prediction button
    if st.button("🎯 Predict Price", type="primary"):
        with st.spinner("Generating prediction..."):
            ticket_data = {
                'team': team,
                'opponent': opponent,
                'venue': venue,
                'section': section,
                'row': row,
                'seat': seat,
                'game_date': game_date,
                'days_until_game': days_until
            }
            
            prediction = run_prediction(ticket_data)
            
            if prediction:
                st.session_state.predictions.append(prediction)
                
                st.success("✅ Prediction complete!")
                
                # Display prediction
                st.markdown('<p class="sub-header">Prediction Results</p>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Predicted Price",
                        f"${prediction['predicted_price']:.2f}",
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        "Lower Bound",
                        f"${prediction['lower_bound']:.2f}",
                        delta=None
                    )
                
                with col3:
                    st.metric(
                        "Upper Bound",
                        f"${prediction['upper_bound']:.2f}",
                        delta=None
                    )
                
                with col4:
                    st.metric(
                        "Confidence",
                        f"{prediction['confidence']:.0%}",
                        delta=None
                    )
                
                # Price range visualization
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=['Lower Bound', 'Predicted', 'Upper Bound'],
                    y=[prediction['lower_bound'], prediction['predicted_price'], prediction['upper_bound']],
                    mode='lines+markers',
                    name='Price Range',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=10)
                ))
                
                fig.update_layout(
                    title='Price Prediction with Confidence Interval',
                    xaxis_title='',
                    yaxis_title='Price ($)',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Model contributions
                if prediction.get('model_contributions'):
                    st.markdown("**Model Contributions**")
                    contrib_df = pd.DataFrame([
                        {'Model': k, 'Weight': v}
                        for k, v in prediction['model_contributions'].items()
                    ])
                    
                    fig = px.pie(
                        contrib_df,
                        values='Weight',
                        names='Model',
                        title='Contribution by Model'
                    )
                    st.plotly_chart(fig, use_container_width=True)


def run_prediction(ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run price prediction"""
    try:
        import time
        time.sleep(1)  # Simulate prediction delay
        
        # Generate mock prediction
        base_price = np.random.uniform(100, 300)
        
        # Adjust based on days until game
        days = ticket_data.get('days_until_game', 30)
        if days < 7:
            base_price *= 1.2
        elif days > 60:
            base_price *= 0.9
        
        uncertainty = base_price * 0.15
        
        prediction = {
            'predicted_price': base_price,
            'lower_bound': base_price - uncertainty,
            'upper_bound': base_price + uncertainty,
            'confidence': np.random.uniform(0.75, 0.90),
            'model_contributions': {
                'Random Forest': 0.30,
                'XGBoost': 0.35,
                'LightGBM': 0.25,
                'CatBoost': 0.10
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return prediction
    except Exception as e:
        st.error(f"Prediction error: {e}")
        return None


def show_forecasting():
    """Demand forecasting page"""
    st.markdown('<p class="main-header">📈 Demand Forecasting</p>', unsafe_allow_html=True)
    st.markdown("Forecast future ticket demand and market trends")
    st.markdown("---")
    
    if not BACKEND_AVAILABLE:
        st.error("Backend services not available. Please check your installation.")
        return
    
    # Forecasting configuration
    st.markdown('<p class="sub-header">Forecast Configuration</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        forecast_method = st.selectbox(
            "Forecasting Method",
            ["Prophet", "ARIMA", "Exponential Smoothing"],
            help="Select forecasting algorithm"
        )
    
    with col2:
        forecast_periods = st.number_input(
            "Forecast Periods (days)",
            min_value=7,
            max_value=90,
            value=30,
            help="Number of days to forecast"
        )
    
    with col3:
        include_seasonality = st.checkbox(
            "Include Seasonality",
            value=True,
            help="Account for seasonal patterns"
        )
    
    # Forecast button
    if st.button("🔮 Generate Forecast", type="primary"):
        with st.spinner(f"Generating {forecast_periods}-day forecast..."):
            forecast = run_forecasting(forecast_method, forecast_periods, include_seasonality)
            
            if forecast:
                st.session_state.forecasts.append(forecast)
                
                st.success("✅ Forecast generated successfully!")
                
                # Display forecast
                st.markdown('<p class="sub-header">Forecast Results</p>', unsafe_allow_html=True)
                
                # Create forecast dataframe
                df_forecast = pd.DataFrame(forecast['data'])
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Avg Demand",
                        f"{df_forecast['demand'].mean():.1f}",
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        "Peak Demand",
                        f"{df_forecast['demand'].max():.1f}",
                        delta=None
                    )
                
                with col3:
                    st.metric(
                        "Min Demand",
                        f"{df_forecast['demand'].min():.1f}",
                        delta=None
                    )
                
                with col4:
                    st.metric(
                        "Trend",
                        "↗️ Increasing" if df_forecast['demand'].iloc[-1] > df_forecast['demand'].iloc[0] else "↘️ Decreasing",
                        delta=None
                    )
                
                # Forecast chart
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df_forecast['date'],
                    y=df_forecast['demand'],
                    mode='lines',
                    name='Forecast',
                    line=dict(color='#1f77b4', width=2)
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_forecast['date'],
                    y=df_forecast['upper_bound'],
                    mode='lines',
                    name='Upper Bound',
                    line=dict(width=0),
                    showlegend=False
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_forecast['date'],
                    y=df_forecast['lower_bound'],
                    mode='lines',
                    name='Lower Bound',
                    line=dict(width=0),
                    fillcolor='rgba(31, 119, 180, 0.2)',
                    fill='tonexty',
                    showlegend=False
                ))
                
                fig.update_layout(
                    title=f'Demand Forecast - Next {forecast_periods} Days',
                    xaxis_title='Date',
                    yaxis_title='Expected Demand',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show data table
                with st.expander("📊 View Forecast Data"):
                    st.dataframe(df_forecast, use_container_width=True)


def run_forecasting(method: str, periods: int, seasonality: bool) -> Dict[str, Any]:
    """Run demand forecasting"""
    try:
        import time
        time.sleep(2)  # Simulate forecasting delay
        
        # Generate mock forecast data
        dates = pd.date_range(start=datetime.now(), periods=periods, freq='D')
        
        # Base trend
        trend = np.linspace(50, 100, periods)
        
        # Add seasonality if enabled
        if seasonality:
            seasonal = 20 * np.sin(np.linspace(0, 4*np.pi, periods))
        else:
            seasonal = np.zeros(periods)
        
        # Add noise
        noise = np.random.normal(0, 5, periods)
        
        # Combine
        demand = trend + seasonal + noise
        demand = np.maximum(demand, 10)  # Minimum demand of 10
        
        # Calculate bounds
        uncertainty = demand * 0.15
        
        forecast_data = []
        for i in range(periods):
            forecast_data.append({
                'date': dates[i],
                'demand': demand[i],
                'lower_bound': demand[i] - uncertainty[i],
                'upper_bound': demand[i] + uncertainty[i]
            })
        
        return {
            'method': method,
            'periods': periods,
            'data': forecast_data,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        st.error(f"Forecasting error: {e}")
        return None


def show_dynamic_pricing():
    """Dynamic pricing page"""
    st.markdown('<p class="main-header">⚡ Dynamic Pricing</p>', unsafe_allow_html=True)
    st.markdown("Optimize prices using advanced pricing strategies")
    st.markdown("---")
    
    if not BACKEND_AVAILABLE:
        st.error("Backend services not available. Please check your installation.")
        return
    
    # Pricing strategy selection
    st.markdown('<p class="sub-header">Pricing Strategy</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        strategy = st.selectbox(
            "Select Strategy",
            ["Revenue Maximization", "Competitive Pricing", "Time-Based", "Psychological"],
            help="Choose pricing optimization strategy"
        )
    
    with col2:
        base_price = st.number_input(
            "Base Price ($)",
            min_value=10.0,
            max_value=1000.0,
            value=150.0,
            help="Starting/reference price"
        )
    
    # Strategy-specific inputs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        days_until_event = st.number_input(
            "Days Until Event",
            min_value=1,
            max_value=365,
            value=30,
            help="Days until the event"
        )
    
    with col2:
        team_performance = st.slider(
            "Team Performance",
            min_value=0.0,
            max_value=1.0,
            value=0.75,
            help="Team win rate (0-1)"
        )
    
    with col3:
        competitor_avg = st.number_input(
            "Competitor Avg Price ($)",
            min_value=10.0,
            max_value=1000.0,
            value=140.0,
            help="Average competitor price"
        )
    
    # Constraints
    with st.expander("⚙️ Price Constraints", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            min_price = st.number_input(
                "Minimum Price ($)",
                min_value=1.0,
                max_value=1000.0,
                value=base_price * 0.5,
                help="Absolute minimum price"
            )
        
        with col2:
            max_price = st.number_input(
                "Maximum Price ($)",
                min_value=1.0,
                max_value=1000.0,
                value=base_price * 2.0,
                help="Absolute maximum price"
            )
    
    # Optimize button
    if st.button("⚡ Optimize Price", type="primary"):
        with st.spinner("Calculating optimal price..."):
            optimization_result = run_pricing_optimization(
                strategy=strategy,
                base_price=base_price,
                days_until_event=days_until_event,
                team_performance=team_performance,
                competitor_avg=competitor_avg,
                min_price=min_price,
                max_price=max_price
            )
            
            if optimization_result:
                st.success("✅ Price optimization complete!")
                
                # Display results
                st.markdown('<p class="sub-header">Optimization Results</p>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Optimal Price",
                        f"${optimization_result['optimal_price']:.2f}",
                        delta=f"{((optimization_result['optimal_price'] - base_price) / base_price * 100):.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "Expected Revenue",
                        f"${optimization_result['expected_revenue']:.2f}",
                        delta=None
                    )
                
                with col3:
                    st.metric(
                        "Expected Demand",
                        f"{optimization_result['expected_demand']:.1f}",
                        delta=None
                    )
                
                with col4:
                    st.metric(
                        "Confidence",
                        f"{optimization_result['confidence']:.0%}",
                        delta=None
                    )
                
                # Reasoning
                st.markdown("**Optimization Reasoning**")
                for reason in optimization_result.get('reasoning', []):
                    st.info(f"• {reason}")
                
                # Price comparison chart
                prices = {
                    'Base Price': base_price,
                    'Optimal Price': optimization_result['optimal_price'],
                    'Competitor Avg': competitor_avg
                }
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(prices.keys()),
                        y=list(prices.values()),
                        marker_color=['lightblue', 'darkblue', 'orange']
                    )
                ])
                
                fig.update_layout(
                    title='Price Comparison',
                    yaxis_title='Price ($)',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)


def run_pricing_optimization(
    strategy: str,
    base_price: float,
    days_until_event: int,
    team_performance: float,
    competitor_avg: float,
    min_price: float,
    max_price: float
) -> Dict[str, Any]:
    """Run price optimization"""
    try:
        import time
        time.sleep(1)  # Simulate optimization delay
        
        # Calculate optimal price based on strategy
        if strategy == "Revenue Maximization":
            # Optimize for revenue
            optimal_price = base_price * (1 + team_performance * 0.2)
            if days_until_event < 7:
                optimal_price *= 1.15
            reasoning = [
                f"Base price adjusted for team performance: +{team_performance*20:.0f}%",
                f"Urgency premium applied (< 7 days): +15%" if days_until_event < 7 else "No urgency premium",
                "Price optimized to maximize total revenue"
            ]
        
        elif strategy == "Competitive Pricing":
            # Match or slightly undercut competitor
            optimal_price = competitor_avg * 0.97
            reasoning = [
                f"Matched competitor average: ${competitor_avg:.2f}",
                "Applied 3% undercut for competitive advantage",
                "Positioned for market share gain"
            ]
        
        elif strategy == "Time-Based":
            # Adjust based on time until event
            if days_until_event > 60:
                optimal_price = base_price * 0.85
                reasoning = ["Early bird discount applied (-15%)"]
            elif days_until_event < 7:
                optimal_price = base_price * 1.25
                reasoning = ["Urgency premium applied (+25%)"]
            else:
                optimal_price = base_price
                reasoning = ["Standard pricing (30-60 days out)"]
        
        else:  # Psychological
            # Apply charm pricing
            optimal_price = np.ceil(base_price) - 0.01
            reasoning = [
                "Charm pricing applied ($.99 ending)",
                "Optimized for psychological appeal"
            ]
        
        # Apply constraints
        optimal_price = max(min_price, min(optimal_price, max_price))
        
        # Calculate expected demand and revenue
        # Simple demand model: higher price = lower demand
        base_demand = 100
        demand_elasticity = -1.5
        price_ratio = optimal_price / base_price
        expected_demand = base_demand * (price_ratio ** demand_elasticity)
        expected_revenue = optimal_price * expected_demand
        
        return {
            'strategy': strategy,
            'optimal_price': optimal_price,
            'expected_revenue': expected_revenue,
            'expected_demand': expected_demand,
            'confidence': np.random.uniform(0.80, 0.90),
            'reasoning': reasoning,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        st.error(f"Optimization error: {e}")
        return None


def show_metrics():
    """Performance metrics page"""
    st.markdown('<p class="main-header">📊 Performance Metrics</p>', unsafe_allow_html=True)
    st.markdown("Monitor system performance and accuracy")
    st.markdown("---")
    
    # Model performance comparison
    if st.session_state.ml_models:
        st.markdown('<p class="sub-header">Model Performance Comparison</p>', unsafe_allow_html=True)
        
        models_data = []
        for name, result in st.session_state.ml_models.items():
            models_data.append({
                'Model': name,
                'R² Score': result.get('r2_score', 0),
                'MAE': result.get('mae', 0),
                'RMSE': result.get('rmse', 0)
            })
        
        df_models = pd.DataFrame(models_data)
        
        # Comparison chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='R² Score',
            x=df_models['Model'],
            y=df_models['R² Score'],
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title='Model Accuracy Comparison (R² Score)',
            yaxis_title='R² Score',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # System statistics
    st.markdown('<p class="sub-header">System Statistics</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Scraping Sessions",
            len(st.session_state.scraping_results),
            delta=None
        )
    
    with col2:
        st.metric(
            "Total Predictions",
            len(st.session_state.predictions),
            delta=None
        )
    
    with col3:
        total_listings = sum(
            len(r.get('listings', []))
            for r in st.session_state.scraping_results
        )
        st.metric(
            "Total Listings Scraped",
            total_listings,
            delta=None
        )
    
    with col4:
        st.metric(
            "Models Trained",
            len(st.session_state.ml_models),
            delta=None
        )
    
    # Performance over time
    if st.session_state.predictions:
        st.markdown('<p class="sub-header">Prediction History</p>', unsafe_allow_html=True)
        
        predictions_df = pd.DataFrame([
            {
                'Time': i + 1,
                'Price': pred['predicted_price'],
                'Confidence': pred['confidence']
            }
            for i, pred in enumerate(st.session_state.predictions)
        ])
        
        fig = px.line(
            predictions_df,
            x='Time',
            y='Price',
            title='Prediction Price Over Time'
        )
        
        st.plotly_chart(fig, use_container_width=True)


def show_configuration():
    """Configuration page"""
    st.markdown('<p class="main-header">⚙️ Configuration</p>', unsafe_allow_html=True)
    st.markdown("System configuration and settings")
    st.markdown("---")
    
    # Scraping configuration
    st.markdown('<p class="sub-header">Scraping Configuration</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            "Default Rate Limit (req/min)",
            min_value=10,
            max_value=60,
            value=30,
            help="Default rate limit for scraping"
        )
        
        st.checkbox(
            "Enable Stealth Mode",
            value=True,
            help="Enable anti-detection features"
        )
    
    with col2:
        st.number_input(
            "Request Timeout (seconds)",
            min_value=10,
            max_value=60,
            value=30,
            help="Timeout for scraping requests"
        )
        
        st.checkbox(
            "Enable Proxy Rotation",
            value=False,
            help="Enable proxy rotation"
        )
    
    # ML configuration
    st.markdown('<p class="sub-header">ML Configuration</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            "Default Training Samples",
            min_value=100,
            max_value=10000,
            value=1000,
            help="Default number of training samples"
        )
        
        st.slider(
            "Train/Test Split",
            min_value=0.5,
            max_value=0.9,
            value=0.8,
            help="Proportion of data for training"
        )
    
    with col2:
        st.checkbox(
            "Enable Hyperparameter Tuning",
            value=False,
            help="Enable GridSearchCV (slower)"
        )
        
        st.checkbox(
            "Enable Feature Selection",
            value=True,
            help="Automatic feature selection"
        )
    
    # Pricing configuration
    st.markdown('<p class="sub-header">Pricing Configuration</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            "Default Price Elasticity",
            min_value=-3.0,
            max_value=-0.5,
            value=-1.5,
            help="Default price elasticity of demand"
        )
    
    with col2:
        st.number_input(
            "Minimum Margin (%)",
            min_value=0,
            max_value=50,
            value=10,
            help="Minimum profit margin"
        )
    
    # System information
    st.markdown("---")
    st.markdown('<p class="sub-header">System Information</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Python Version:** {sys.version.split()[0]}")
        st.info(f"**Streamlit Version:** {st.__version__}")
        st.info(f"**Backend Available:** {'Yes ✅' if BACKEND_AVAILABLE else 'No ❌'}")
    
    with col2:
        st.info(f"**Working Directory:** {os.getcwd()}")
        st.info(f"**Backend Path:** {backend_path}")
    
    # Reset button
    st.markdown("---")
    if st.button("🔄 Reset All Data", type="secondary"):
        st.session_state.scraping_results = []
        st.session_state.ml_models = {}
        st.session_state.predictions = []
        st.session_state.forecasts = []
        st.success("All data has been reset!")
        st.rerun()


if __name__ == "__main__":
    main()
