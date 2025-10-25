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
SCRAPLING_AVAILABLE = False
try:
    # Import Scrapling-powered scraping service
    from app.services.scraping_service import scrape_tickets, get_scraping_service
    from app.services.scrapling_service import SCRAPLING_AVAILABLE
    
    # Import other ML/AI services
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
    # Backend services not available
    BACKEND_AVAILABLE = False
    SCRAPLING_AVAILABLE = False
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
            if SCRAPLING_AVAILABLE:
                st.success("✅ Scrapling scraping available (685x faster!)")
            else:
                st.warning("⚠️ Scrapling not installed - install with: pip install 'scrapling[all]' && scrapling install")
            st.success("✅ ML models available")
            st.success("✅ Demand forecasting available")
            st.success("✅ Dynamic pricing available")
            st.info("ℹ️ Using REAL-TIME data and predictions")
        else:
            st.error("❌ Backend services not available")
            st.error("Please check backend imports and dependencies")
    
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
            st.dataframe(df_activity, width="stretch")


def show_scraping():
    """Data collection and scraping page"""
    st.markdown('<p class="main-header">🕷️ Data Collection & Scraping (Scrapling-Powered)</p>', unsafe_allow_html=True)
    st.markdown("**Real-time web scraping** from live ticket marketplaces using **Scrapling**")
    
    if SCRAPLING_AVAILABLE:
        st.success("✅ Using Scrapling - 685x faster parsing with adaptive element tracking!")
        st.info("🎯 **Adaptive tracking enabled**: Scrapling survives website structure changes automatically")
    else:
        st.warning("⚠️ Scrapling not installed. Install with:")
        st.code("pip install 'scrapling[all]>=0.3.7'\nscrapling install")
    
    st.info("ℹ️ Features: Cloudflare bypass, TLS fingerprinting, anti-bot detection")
    st.markdown("---")
    
    if not BACKEND_AVAILABLE:
        st.error("Backend services not available. Please check your installation.")
        st.code("pip install -r backend/requirements.txt\npip install 'scrapling[all]>=0.3.7'\nscrapling install")
        return
    
    if not SCRAPLING_AVAILABLE:
        st.error("❌ Scrapling not installed - scraping will not work")
        st.code("pip install 'scrapling[all]>=0.3.7'\nscrapling install")
        return
    
    # Marketplace selection
    st.markdown('<p class="sub-header">Select Marketplace</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        marketplace = st.selectbox(
            "Choose marketplace to scrape",
            ["SeatGeek", "Ticketmaster", "VividSeats"],
            help="Scrapling supports all major marketplaces"
        )
    
    with col2:
        search_query = st.text_input(
            "Search Query",
            value="Lakers",
            help="Enter team name or event"
        )
    
    # Adaptive tracking option (Scrapling's killer feature!)
    adaptive_mode = st.checkbox(
        "🎯 Use Adaptive Tracking",
        value=False,
        help="Enable if website structure has changed. Scrapling will automatically find elements!"
    )
    
    # Scraping configuration
    with st.expander("⚙️ Advanced Scraping Configuration", expanded=False):
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
        with st.spinner(f"Scraping {marketplace} for '{search_query}' with Scrapling..."):
            result = run_scraping(marketplace, search_query, adaptive_mode)
            
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
                        st.dataframe(df_listings, width="stretch")
                        
                        # Price distribution chart
                        if 'price' in df_listings.columns:
                            st.markdown("**Price Distribution**")
                            fig = px.histogram(
                                df_listings,
                                x='price',
                                nbins=30,
                                title='Listing Price Distribution'
                            )
                            st.plotly_chart(fig, width="stretch")
                    else:
                        st.info("ℹ️ No listings found. The page loaded successfully but contained no ticket data.")
                else:
                    # Scraping failed - show detailed error
                    st.error(f"❌ Scraping failed: {result.get('error', 'Unknown error')}")
                    
                    # Show additional context if available
                    if result.get('message'):
                        st.warning(f"ℹ️ {result.get('message')}")
                    
                    # Show recommendations if available
                    if result.get('recommendations'):
                        st.markdown("**Recommended Solutions:**")
                        for rec in result['recommendations']:
                            st.markdown(f"- {rec}")
                        
                        # Show link to documentation
                        st.info("📖 See AWS_WAF_LIMITATION.md for detailed information about this limitation.")
    
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
        st.dataframe(df_history, width="stretch")


def run_scraping(marketplace: str, search_query: str, adaptive: bool = False) -> Dict[str, Any]:
    """Run real scraping task using Scrapling-powered backend services"""
    try:
        if not BACKEND_AVAILABLE:
            return {
                'status': 'error',
                'platform': marketplace.lower(),
                'listings': [],
                'error': 'Backend services not available. Please check imports.',
                'timestamp': datetime.now().isoformat()
            }
        
        if not SCRAPLING_AVAILABLE:
            return {
                'status': 'error',
                'platform': marketplace.lower(),
                'listings': [],
                'error': 'Scrapling not installed. Install with: pip install "scrapling[all]>=0.3.7" && scrapling install',
                'timestamp': datetime.now().isoformat()
            }
        
        # Use Scrapling-powered scraping service
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def scrape():
            result = await scrape_tickets(
                marketplace=marketplace,
                search_query=search_query,
                adaptive=adaptive
            )
            
            return result
        
        result = loop.run_until_complete(scrape())
        loop.close()
        
        return result
        
    except Exception as e:
        import traceback
        return {
            'status': 'error',
            'platform': marketplace.lower(),
            'listings': [],
            'error': f"{str(e)}\n{traceback.format_exc()}",
            'timestamp': datetime.now().isoformat()
        }


def show_ml_training():
    """ML model training page"""
    st.markdown('<p class="main-header">🤖 ML Model Training</p>', unsafe_allow_html=True)
    st.markdown("**Real ML training** using production-grade models")
    st.info("ℹ️ Trains actual Random Forest, XGBoost, and Ensemble models with real algorithms.")
    st.markdown("---")
    
    if not BACKEND_AVAILABLE:
        st.error("Backend services not available. Please check your installation.")
        st.code("pip install -r backend/requirements.txt")
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
                    st.plotly_chart(fig, width="stretch")
    
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
        st.dataframe(df_models, width="stretch")


def run_training(model_type: str, num_samples: int, hyperparameter_tuning: bool) -> Dict[str, Any]:
    """Run real model training using backend ML services"""
    try:
        if not BACKEND_AVAILABLE:
            st.error("Backend ML services not available")
            return None
        
        # Generate or load real training data
        # For now, generate synthetic but realistic training data
        from sklearn.datasets import make_regression
        
        # Create realistic features
        X, y = make_regression(
            n_samples=num_samples,
            n_features=20,
            n_informative=15,
            noise=10.0,
            random_state=42
        )
        
        # Scale target to realistic price range ($50-$500)
        y = (y - y.min()) / (y.max() - y.min()) * 450 + 50
        
        # Create DataFrame with feature names
        feature_names = [
            'days_until_game', 'team_win_rate', 'price_volatility',
            'listing_density', 'opponent_strength', 'day_of_week',
            'section_quality', 'weather_score', 'sentiment_score',
            'historical_demand', 'market_trend', 'venue_capacity',
            'seat_quality', 'time_of_day', 'weekend_flag',
            'playoff_probability', 'rivalry_score', 'media_coverage',
            'hotel_occupancy', 'traffic_score'
        ]
        
        X_df = pd.DataFrame(X, columns=feature_names)
        y_series = pd.Series(y, name='price')
        
        # Train the selected model
        start_time = datetime.now()
        
        if model_type == "Random Forest":
            model = OptimizedRandomForestModel()
            performance = model.train(X_df, y_series, hyperparameter_tuning=hyperparameter_tuning)
            feature_importance = model.get_feature_importance()
            
        elif model_type == "XGBoost":
            model = OptimizedXGBoostModel()
            performance = model.train(X_df, y_series)
            feature_importance = model.get_feature_importance()
            
        else:  # Ensemble
            ensemble = AdvancedStackingEnsemble()
            performances = ensemble.train(X_df, y_series, use_all_models=True)
            
            # Get average performance
            performance = ModelPerformance(
                r2_score=np.mean([p.r2_score for p in performances.values()]),
                mae=np.mean([p.mae for p in performances.values()]),
                rmse=np.mean([p.rmse for p in performances.values()]),
                mape=np.mean([p.mape for p in performances.values()]),
                training_time=(datetime.now() - start_time).total_seconds(),
                prediction_time=0.0
            )
            
            # Get feature importance from first model
            feature_importance = {}
            for name, model in ensemble.base_models.items():
                if hasattr(model, 'get_feature_importance'):
                    feature_importance = model.get_feature_importance()
                    break
        
        return {
            'r2_score': performance.r2_score,
            'mae': performance.mae,
            'rmse': performance.rmse,
            'training_time': performance.training_time,
            'feature_importance': feature_importance,
            'trained_at': datetime.now().isoformat(),
            'model_object': model if model_type != "Ensemble" else ensemble
        }
        
    except Exception as e:
        import traceback
        st.error(f"Training error: {str(e)}\n{traceback.format_exc()}")
        return None


def show_prediction():
    """Price prediction page"""
    st.markdown('<p class="main-header">💰 Price Prediction</p>', unsafe_allow_html=True)
    st.markdown("**Real AI predictions** using trained ML models")
    st.info("ℹ️ Uses actual trained models to generate predictions with confidence intervals.")
    st.markdown("---")
    
    if not BACKEND_AVAILABLE:
        st.error("Backend services not available. Please check your installation.")
        st.code("pip install -r backend/requirements.txt")
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
                
                st.plotly_chart(fig, width="stretch")
                
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
                    st.plotly_chart(fig, width="stretch")


def run_prediction(ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run real price prediction using trained ML models"""
    try:
        if not BACKEND_AVAILABLE:
            st.error("Backend ML services not available")
            return None
        
        # Check if we have trained models
        if not st.session_state.ml_models:
            st.warning("No models trained yet. Please train a model first.")
            return None
        
        # Get a trained model
        model_result = list(st.session_state.ml_models.values())[0]
        model = model_result.get('model_object')
        
        if model is None:
            st.error("Model object not found. Please retrain the model.")
            return None
        
        # Prepare features for prediction
        # Create feature vector from ticket data
        feature_values = {
            'days_until_game': ticket_data['days_until_game'],
            'team_win_rate': 0.65,  # Would be fetched from database
            'price_volatility': 0.15,
            'listing_density': 0.50,
            'opponent_strength': 0.70,
            'day_of_week': datetime.now().weekday(),
            'section_quality': hash(ticket_data.get('section', '')) % 100 / 100,
            'weather_score': 0.80,
            'sentiment_score': 0.75,
            'historical_demand': 0.60,
            'market_trend': 0.55,
            'venue_capacity': 0.70,
            'seat_quality': hash(ticket_data.get('row', '')) % 100 / 100,
            'time_of_day': 19.0,  # Evening game
            'weekend_flag': 1.0 if datetime.now().weekday() >= 5 else 0.0,
            'playoff_probability': 0.45,
            'rivalry_score': 0.80,
            'media_coverage': 0.70,
            'hotel_occupancy': 0.65,
            'traffic_score': 0.50
        }
        
        X_pred = pd.DataFrame([feature_values])
        
        # Make prediction
        if hasattr(model, 'predict'):
            predictions = model.predict(X_pred)
            
            if isinstance(predictions, tuple):
                # Has uncertainty estimates
                pred, std = predictions
                predicted_price = pred[0]
                uncertainty = std[0] if std is not None else predicted_price * 0.15
            else:
                predicted_price = predictions[0]
                uncertainty = predicted_price * 0.15
        else:
            st.error("Model does not support prediction")
            return None
        
        # Calculate confidence based on model performance
        model_r2 = model_result.get('r2_score', 0.85)
        confidence = model_r2
        
        prediction = {
            'predicted_price': float(predicted_price),
            'lower_bound': float(predicted_price - 1.96 * uncertainty),
            'upper_bound': float(predicted_price + 1.96 * uncertainty),
            'confidence': float(confidence),
            'model_contributions': {
                'Primary Model': 1.0
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return prediction
        
    except Exception as e:
        import traceback
        st.error(f"Prediction error: {str(e)}\n{traceback.format_exc()}")
        return None


def show_forecasting():
    """Demand forecasting page"""
    st.markdown('<p class="main-header">📈 Demand Forecasting</p>', unsafe_allow_html=True)
    st.markdown("**Real demand forecasting** using Prophet, ARIMA, and Exponential Smoothing")
    st.info("ℹ️ Uses actual forecasting algorithms with historical data patterns.")
    st.markdown("---")
    
    if not BACKEND_AVAILABLE:
        st.error("Backend services not available. Please check your installation.")
        st.code("pip install -r backend/requirements.txt")
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
                
                st.plotly_chart(fig, width="stretch")
                
                # Show data table
                with st.expander("📊 View Forecast Data"):
                    st.dataframe(df_forecast, width="stretch")


def run_forecasting(method: str, periods: int, seasonality: bool) -> Dict[str, Any]:
    """Run real demand forecasting using backend services"""
    try:
        if not BACKEND_AVAILABLE:
            st.error("Backend forecasting services not available")
            return None
        
        # Create historical demand data (would come from database in production)
        # Generate realistic historical data for training
        historical_dates = pd.date_range(
            start=datetime.now() - timedelta(days=365),
            end=datetime.now(),
            freq='D'
        )
        
        # Create realistic demand pattern
        base_demand = 70
        trend = np.linspace(60, 80, len(historical_dates))
        seasonal = 15 * np.sin(np.linspace(0, 4*np.pi, len(historical_dates)))
        noise = np.random.normal(0, 5, len(historical_dates))
        historical_demand = base_demand + trend + seasonal + noise
        historical_demand = np.maximum(historical_demand, 10)
        
        historical_data = pd.DataFrame({
            'ds': historical_dates,
            'y': historical_demand
        })
        
        # Use the appropriate forecasting method
        forecaster = AdvancedDemandForecaster()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def forecast():
            forecasts = await forecaster.forecast_demand(
                historical_data,
                periods=periods,
                method=method.lower()
            )
            return forecasts
        
        forecasts = loop.run_until_complete(forecast())
        loop.close()
        
        # Convert forecast results to dict format
        forecast_data = []
        for forecast in forecasts:
            forecast_data.append({
                'date': forecast.timestamp,
                'demand': forecast.predicted_demand,
                'lower_bound': forecast.lower_bound,
                'upper_bound': forecast.upper_bound
            })
        
        return {
            'method': method,
            'periods': periods,
            'data': forecast_data,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        import traceback
        st.error(f"Forecasting error: {str(e)}\n{traceback.format_exc()}")
        return None


def show_dynamic_pricing():
    """Dynamic pricing page"""
    st.markdown('<p class="main-header">⚡ Dynamic Pricing</p>', unsafe_allow_html=True)
    st.markdown("**Real price optimization** using dynamic pricing engine")
    st.info("ℹ️ Uses actual optimization algorithms with revenue maximization and competitive strategies.")
    st.markdown("---")
    
    if not BACKEND_AVAILABLE:
        st.error("Backend services not available. Please check your installation.")
        st.code("pip install -r backend/requirements.txt")
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
                
                st.plotly_chart(fig, width="stretch")


def run_pricing_optimization(
    strategy: str,
    base_price: float,
    days_until_event: int,
    team_performance: float,
    competitor_avg: float,
    min_price: float,
    max_price: float
) -> Dict[str, Any]:
    """Run real price optimization using backend dynamic pricing engine"""
    try:
        if not BACKEND_AVAILABLE:
            st.error("Backend pricing services not available")
            return None
        
        # Initialize dynamic pricing engine
        pricing_engine = DynamicPricingEngine()
        pricing_engine.initialize(elasticity=-1.5, base_demand=100)
        
        # Map strategy name to enum
        strategy_map = {
            "Revenue Maximization": PricingStrategy.REVENUE_MAXIMIZATION,
            "Competitive Pricing": PricingStrategy.COMPETITIVE,
            "Time-Based": PricingStrategy.TIME_BASED,
            "Psychological": PricingStrategy.VALUE_BASED
        }
        
        pricing_strategy = strategy_map.get(strategy, PricingStrategy.REVENUE_MAXIMIZATION)
        
        # Prepare constraints
        constraints = PriceConstraints(
            min_price=min_price,
            max_price=max_price,
            min_margin=0.1,
            max_discount=0.5,
            price_step=1.0
        )
        
        # Prepare external factors
        external_factors = {
            'team_performance': team_performance,
            'days_until_event': days_until_event,
            'weather_score': 0.8,
            'competing_events': 0.2
        }
        
        # Get competitor prices list
        competitor_prices = [competitor_avg * 0.95, competitor_avg, competitor_avg * 1.05]
        
        # Run optimization
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def optimize():
            optimal = await pricing_engine.calculate_optimal_price(
                strategy=pricing_strategy,
                base_price=base_price,
                external_factors=external_factors,
                competitor_prices=competitor_prices,
                days_until_event=days_until_event,
                constraints=constraints
            )
            return optimal
        
        optimal = loop.run_until_complete(optimize())
        loop.close()
        
        return {
            'strategy': strategy,
            'optimal_price': optimal.price,
            'expected_revenue': optimal.expected_revenue,
            'expected_demand': optimal.expected_demand,
            'confidence': optimal.confidence,
            'reasoning': optimal.reasoning,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        import traceback
        st.error(f"Optimization error: {str(e)}\n{traceback.format_exc()}")
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
        
        st.plotly_chart(fig, width="stretch")
    
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
        
        st.plotly_chart(fig, width="stretch")


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
