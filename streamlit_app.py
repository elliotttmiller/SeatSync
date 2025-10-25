"""
SeatSync - Advanced Ticket Analytics Platform
Modern, production-ready interface with full Scrapling integration.
"""

import streamlit as st
import pandas as pd
import numpy as np
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import backend services
from app.services.scrapling_scraper import scrape_tickets, get_scraper_service
from app.services.enhanced_ml_models import (
    AdvancedStackingEnsemble,
    OptimizedRandomForestModel,
    OptimizedXGBoostModel,
    ModelPerformance
)
from app.services.demand_forecasting import AdvancedDemandForecaster, DemandForecast
from app.services.dynamic_pricing import (
    DynamicPricingEngine,
    PricingStrategy,
    PriceConstraints,
    OptimalPrice
)

# Page configuration
st.set_page_config(
    page_title="SeatSync Analytics",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Material Design 3 CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #f0f0f0;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        border: none;
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'scraping_results' not in st.session_state:
    st.session_state.scraping_results = []
if 'ml_models' not in st.session_state:
    st.session_state.ml_models = {}

def main():
    st.sidebar.markdown("# 🎫 SeatSync")
    page = st.sidebar.radio("", ["🏠 Dashboard", "🕷️ Scraping", "📊 Analytics"])
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🕷️ Scraping":
        show_scraping()
    else:
        show_analytics()

def show_dashboard():
    st.markdown('<div class="main-title">🎫 SeatSync Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Full Scrapling Stealth Mode Active</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Scraping Sessions", len(st.session_state.scraping_results))
    with col2:
        total = sum(r.get('total_listings', 0) for r in st.session_state.scraping_results)
        st.metric("Total Listings", f"{total:,}")
    with col3:
        st.metric("ML Models", len(st.session_state.ml_models))
    with col4:
        st.metric("Status", "✅ ACTIVE")

def show_scraping():
    st.markdown('<div class="main-title">🕷️ Multi-Marketplace Scraping</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">All marketplaces • Full stealth mode</div>', unsafe_allow_html=True)
    
    search_query = st.text_input("Search Query", value="Lakers")
    
    if st.button("🚀 Start Scraping", type="primary"):
        with st.spinner(f'Scraping all marketplaces for "{search_query}"...'):
            result = run_scraping(search_query)
            
            if result:
                st.session_state.scraping_results.append(result)
                st.success(f"✅ Found {result.get('total_listings', 0)} listings!")
                
                # Show results
                per_marketplace = result.get('per_marketplace', {})
                for mp, mp_result in per_marketplace.items():
                    with st.expander(f"{mp.upper()} - {len(mp_result.get('listings', []))} listings"):
                        if mp_result.get('status') == 'success':
                            listings = mp_result.get('listings', [])
                            if listings:
                                df = pd.DataFrame(listings[:50])
                                st.dataframe(df, use_container_width=True)

def run_scraping(search_query: str) -> Dict[str, Any]:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(scrape_tickets(search_query=search_query))
        loop.close()
        return result
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'total_listings': 0, 'listings': []}

def show_analytics():
    st.markdown('<div class="main-title">📊 Analytics</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sessions", len(st.session_state.scraping_results))
    with col2:
        total = sum(r.get('total_listings', 0) for r in st.session_state.scraping_results)
        st.metric("Listings", total)
    with col3:
        st.metric("Models", len(st.session_state.ml_models))

if __name__ == "__main__":
    main()
