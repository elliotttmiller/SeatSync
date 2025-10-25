"""
SeatSync - Advanced Ticket Analytics Platform
Modern dark theme interface inspired by ChatGPT
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
from app.services.scrapling_scraper import scrape_tickets
from app.services.enhanced_ml_models import (
    OptimizedRandomForestModel,
    OptimizedXGBoostModel,
    AdvancedStackingEnsemble,
    ModelPerformance
)
from app.services.demand_forecasting import AdvancedDemandForecaster, DemandForecast
from app.services.dynamic_pricing import (
    DynamicPricingEngine,
    PricingStrategy,
    PriceConstraints
)

# Page configuration
st.set_page_config(
    page_title="SeatSync Analytics",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Dark Theme - ChatGPT Inspired
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp { background-color: #1E1E1E; }
    * { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif; }
    .main { background-color: #1E1E1E; color: #ECECEC; padding: 2rem; }
    
    [data-testid="stSidebar"] {
        background-color: #2D2D2D;
        border-right: 1px solid #3E3E3E;
    }
    [data-testid="stSidebar"] * { color: #ECECEC !important; }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 600;
        color: #ECECEC;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    .sub-title {
        font-size: 1rem;
        color: #B4B4B4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #ECECEC;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    .stButton>button {
        background-color: #10A37F;
        color: white;
        font-weight: 500;
        font-size: 0.95rem;
        padding: 0.625rem 1.5rem;
        border-radius: 8px;
        border: none;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #0D8B6C;
        box-shadow: 0 2px 8px rgba(16, 163, 127, 0.3);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 600;
        color: #10A37F;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        font-weight: 500;
        color: #B4B4B4;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    h1, h2, h3, h4, h5, h6, p, span, div { color: #ECECEC; }
    
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background-color: #2D2D2D;
        color: #ECECEC;
        border: 1px solid #3E3E3E;
        border-radius: 8px;
    }
    .stTextInput input:focus {
        border-color: #10A37F;
        box-shadow: 0 0 0 1px #10A37F;
    }
    
    .info-msg {
        background-color: #1E3A5F;
        color: #5B9BD5;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #5B9BD5;
        margin: 1rem 0;
    }
    
    .streamlit-expanderHeader {
        background-color: #2D2D2D;
        border: 1px solid #3E3E3E;
        border-radius: 8px;
        color: #ECECEC;
    }
    
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #1E1E1E; }
    ::-webkit-scrollbar-thumb { background: #3E3E3E; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #4E4E4E; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'scraping_results' not in st.session_state:
    st.session_state.scraping_results = []
if 'ml_models' not in st.session_state:
    st.session_state.ml_models = {}

def main():
    st.sidebar.markdown("# 🎫 SeatSync")
    st.sidebar.markdown("**Analytics Platform**")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio("", ["🏠 Dashboard", "🕷️ Scraping", "📊 Analytics"])
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='padding: 1rem; background: rgba(16,163,127,0.1); border-radius: 8px; border: 1px solid rgba(16,163,127,0.3);'>
        <div style='color: #10A37F; font-weight: 600; margin-bottom: 0.5rem;'>✨ Full Stealth Mode</div>
        <div style='font-size: 0.85rem; color: #B4B4B4;'>All advanced features active</div>
    </div>
    """, unsafe_allow_html=True)
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🕷️ Scraping":
        show_scraping()
    else:
        show_analytics()

def show_dashboard():
    st.markdown('<div class="main-title">🎫 SeatSync Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Advanced Ticket Intelligence • Full Stealth Mode Active</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🕷️ Sessions", len(st.session_state.scraping_results))
    with col2:
        total = sum(r.get('total_listings', 0) for r in st.session_state.scraping_results)
        st.metric("📊 Listings", f"{total:,}")
    with col3:
        st.metric("🤖 Models", len(st.session_state.ml_models))
    with col4:
        st.metric("⚡ Status", "ACTIVE")
    
    if st.session_state.scraping_results:
        st.markdown('<div class="section-header">Recent Activity</div>', unsafe_allow_html=True)
        latest = st.session_state.scraping_results[-1]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Latest Scrape", f"{latest.get('total_listings', 0)} listings")
        with col2:
            summary = latest.get('summary', {})
            st.metric("Success Rate", f"{summary.get('successful', 0)}/{summary.get('total', 0)}")
        with col3:
            st.metric("Status", latest.get('status', 'unknown').upper())

def show_scraping():
    st.markdown('<div class="main-title">🕷️ Multi-Marketplace Scraping</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Real-time data • All marketplaces • Full stealth mode</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-msg'>
        ✨ <strong>Full Stealth Mode Active</strong> - All advanced features enabled<br>
        🎯 Concurrent scraping across 4 marketplaces
    </div>
    """, unsafe_allow_html=True)
    
    search_query = st.text_input(
        "Search Query",
        value="Lakers",
        placeholder="Enter team name or event..."
    )
    
    if st.button("🚀 Start Scraping", type="primary"):
        if not search_query:
            st.error("❌ Please enter a search query")
            return
        
        with st.spinner(f'Scraping all marketplaces for "{search_query}"...'):
            result = run_scraping(search_query)
            
            if result:
                st.session_state.scraping_results.append(result)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Listings", result.get('total_listings', 0))
                with col2:
                    summary = result.get('summary', {})
                    st.metric("Successful", f"{summary.get('successful', 0)}/{summary.get('total', 0)}")
                with col3:
                    status = result.get('status', 'unknown')
                    st.metric("Status", f"{'✅' if status == 'success' else '⚠️'} {status.upper()}")
                
                st.markdown('<div class="section-header">Marketplace Results</div>', unsafe_allow_html=True)
                
                per_marketplace = result.get('per_marketplace', {})
                for mp, mp_result in per_marketplace.items():
                    with st.expander(f"📊 {mp.upper()} - {len(mp_result.get('listings', []))} listings", expanded=True):
                        if mp_result.get('status') == 'success':
                            listings = mp_result.get('listings', [])
                            if listings:
                                df = pd.DataFrame(listings[:50])
                                st.dataframe(df, use_container_width=True)
                        else:
                            st.error(f"❌ {mp_result.get('error', 'Unknown error')}")
                
                all_listings = result.get('listings', [])
                if all_listings:
                    st.markdown('<div class="section-header">Price Distribution</div>', unsafe_allow_html=True)
                    df_all = pd.DataFrame(all_listings)
                    if 'price' in df_all.columns and 'platform' in df_all.columns:
                        fig = px.histogram(
                            df_all, x='price', color='platform', nbins=30,
                            title='Price Distribution', barmode='overlay', opacity=0.7
                        )
                        fig.update_layout(
                            template='plotly_dark',
                            paper_bgcolor='#1E1E1E',
                            plot_bgcolor='#2D2D2D',
                            font_color='#ECECEC',
                            height=500
                        )
                        st.plotly_chart(fig, use_container_width=True)

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
    st.markdown('<div class="main-title">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Performance metrics and insights</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sessions", len(st.session_state.scraping_results))
    with col2:
        total = sum(r.get('total_listings', 0) for r in st.session_state.scraping_results)
        st.metric("Listings", f"{total:,}")
    with col3:
        st.metric("Models", len(st.session_state.ml_models))
    with col4:
        st.metric("Predictions", "0")

if __name__ == "__main__":
    main()
