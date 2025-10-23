# SeatSync Streamlit Development Dashboard

## Overview

This Streamlit application provides a professional, modern UI for testing and validating the SeatSync backend during the development phase. It allows you to interact with all advanced features without needing the full React production frontend.

## Features

### 🏠 Home Dashboard
- System status overview
- Quick statistics
- Recent activity feed
- Component availability check

### 🕷️ Data Collection & Scraping
- Test web scraping from marketplaces (StubHub, SeatGeek)
- Configure scraping parameters
- View scraped data in real-time
- Analyze price distributions
- Track scraping history

### 🤖 ML Model Training
- Train individual models (Random Forest, XGBoost)
- Train ensemble models
- Configure hyperparameter tuning
- View training performance metrics
- Analyze feature importance

### 💰 Price Prediction
- Get AI-powered price predictions
- Input ticket details
- View confidence intervals
- Analyze model contributions
- Compare predictions

### 📈 Demand Forecasting
- Generate demand forecasts (Prophet, ARIMA, Exponential Smoothing)
- Configure forecast periods
- View forecast charts with confidence bands
- Analyze seasonal patterns
- Export forecast data

### ⚡ Dynamic Pricing
- Optimize prices using multiple strategies
- Revenue maximization
- Competitive pricing
- Time-based pricing
- Psychological pricing
- Configure price constraints
- View optimization reasoning

### 📊 Performance Metrics
- Model performance comparison
- System statistics
- Prediction history
- Scraping analytics

### ⚙️ Configuration
- Adjust scraping settings
- ML configuration
- Pricing parameters
- System information
- Reset data

## Installation

### Prerequisites

```bash
# Ensure Python 3.10+ is installed
python --version

# Navigate to project directory
cd /path/to/SeatSync
```

### Install Dependencies

```bash
# Install backend dependencies (includes Streamlit)
pip install -r backend/requirements.txt
```

## Running the Application

### Option 1: Using the Shell Script (Recommended)

```bash
# Make the script executable (first time only)
chmod +x run_streamlit.sh

# Run the application
./run_streamlit.sh
```

### Option 2: Direct Streamlit Command

```bash
# From the project root directory
streamlit run streamlit_app.py
```

### Option 3: Custom Port

```bash
# Run on a specific port
streamlit run streamlit_app.py --server.port 8502
```

## Accessing the Dashboard

Once started, the application will be available at:

```
http://localhost:8501
```

Your browser should automatically open to this URL. If not, manually navigate to it.

## Usage Guide

### 1. Testing Data Scraping

1. Navigate to **🕷️ Data Collection & Scraping**
2. Select marketplace (StubHub or SeatGeek for testing)
3. Enter search query (e.g., "Lakers", "Warriors")
4. Configure scraping settings (optional)
5. Click **🚀 Start Scraping**
6. View results: listings, price distribution, statistics

### 2. Training ML Models

1. Navigate to **🤖 ML Model Training**
2. Select model type (Random Forest, XGBoost, or Ensemble)
3. Configure training data (use mock data for testing)
4. Optionally enable hyperparameter tuning
5. Click **🚀 Start Training**
6. View training metrics: R² score, MAE, RMSE
7. Analyze feature importance

### 3. Making Price Predictions

1. Navigate to **💰 Price Prediction**
2. Ensure models are trained (train in previous step)
3. Enter ticket information:
   - Team, opponent, venue
   - Section, row, seat
   - Game date
4. Click **🎯 Predict Price**
5. View prediction with confidence intervals
6. Analyze model contributions

### 4. Forecasting Demand

1. Navigate to **📈 Demand Forecasting**
2. Select forecasting method (Prophet recommended)
3. Set forecast period (7-90 days)
4. Enable seasonality (recommended)
5. Click **🔮 Generate Forecast**
6. View forecast chart with confidence bands
7. Export data if needed

### 5. Optimizing Prices

1. Navigate to **⚡ Dynamic Pricing**
2. Select pricing strategy
3. Enter base price and ticket details
4. Configure price constraints
5. Click **⚡ Optimize Price**
6. View optimal price and expected revenue
7. Review optimization reasoning

### 6. Monitoring Performance

1. Navigate to **📊 Performance Metrics**
2. View model comparison charts
3. Check system statistics
4. Analyze prediction history
5. Monitor accuracy trends

## Configuration

### Scraping Settings

- **Rate Limit**: Requests per minute (default: 30)
- **Stealth Mode**: Enable anti-detection (recommended: ON)
- **Proxy Rotation**: Use proxies (default: OFF for testing)
- **Request Timeout**: Maximum wait time (default: 30s)

### ML Settings

- **Training Samples**: Number of samples for training (default: 1000)
- **Train/Test Split**: Proportion for training (default: 0.8)
- **Hyperparameter Tuning**: Enable GridSearchCV (slower but better)
- **Feature Selection**: Automatic feature selection (recommended: ON)

### Pricing Settings

- **Price Elasticity**: Demand sensitivity to price (default: -1.5)
- **Minimum Margin**: Minimum profit margin % (default: 10%)
- **Price Constraints**: Min/max price bounds

## Mock Data vs. Real Data

### Current Implementation

For testing purposes, the app uses **mock data** to simulate:
- Scraped listings with realistic prices
- Training data for ML models
- Performance metrics

### Transitioning to Real Data

To use real scraping and data:

1. Configure API keys in `.env`:
   ```bash
   STUBHUB_API_KEY=your_key
   SEATGEEK_CLIENT_ID=your_id
   SEATGEEK_CLIENT_SECRET=your_secret
   ```

2. Update the scraping functions in `streamlit_app.py` to use actual scrapers:
   ```python
   # Replace mock data with:
   from app.services.enhanced_scraping import get_scraping_engine
   
   scraping_engine = await get_scraping_engine()
   context = await scraping_engine.create_stealth_context()
   # ... actual scraping logic
   ```

3. Connect to production database for real training data

## Troubleshooting

### Port Already in Use

```bash
# Kill the process using port 8501
lsof -ti:8501 | xargs kill -9

# Or use a different port
streamlit run streamlit_app.py --server.port 8502
```

### Backend Import Errors

```bash
# Ensure backend path is correct
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Missing Dependencies

```bash
# Install missing packages
pip install streamlit plotly pandas numpy
```

### Streamlit Not Found

```bash
# Install Streamlit
pip install streamlit

# Or use pipx
pipx install streamlit
```

## Development Workflow

### Recommended Testing Flow

1. **Start Fresh**
   - Launch Streamlit app
   - Check system status on Home page

2. **Test Scraping**
   - Scrape 1-2 marketplaces
   - Verify data quality
   - Check performance

3. **Train Models**
   - Start with Random Forest (fastest)
   - Test XGBoost
   - Compare results

4. **Make Predictions**
   - Test with various ticket inputs
   - Validate predictions make sense
   - Check confidence levels

5. **Forecast Demand**
   - Generate 30-day forecast
   - Verify seasonality patterns
   - Export results

6. **Optimize Pricing**
   - Test different strategies
   - Compare outputs
   - Validate constraints

7. **Review Metrics**
   - Check model accuracy
   - Monitor system performance
   - Identify improvements

### Iterative Testing

- Use the **Reset All Data** button in Configuration to start fresh
- Test different parameter combinations
- Document findings and performance
- Compare against expected benchmarks

## Performance Expectations

### Response Times

- **Scraping**: 2-5 seconds per marketplace
- **Model Training**: 30-150 seconds depending on model
- **Predictions**: < 1 second
- **Forecasting**: 2-3 seconds
- **Price Optimization**: 1-2 seconds

### Accuracy Targets

- **Random Forest**: R² ≈ 0.87
- **XGBoost**: R² ≈ 0.89
- **Ensemble**: R² ≈ 0.91
- **MAE**: < $15
- **RMSE**: < $25

## Best Practices

### For Development

1. **Start Simple**: Test with mock data first
2. **Incremental Testing**: Test one component at a time
3. **Document Findings**: Keep notes on performance
4. **Compare Baselines**: Track improvements over time
5. **Clean Up**: Reset data between major tests

### For Production Migration

1. **Validate All Components**: Ensure everything works end-to-end
2. **Performance Benchmarks**: Meet target metrics
3. **Error Handling**: Test error scenarios
4. **Load Testing**: Test with realistic data volumes
5. **Security**: Review API keys and data handling

## Next Steps

After validating the Streamlit app:

1. **Data Infrastructure**: Deploy real scraping infrastructure
2. **Database Integration**: Connect to production database
3. **API Integration**: Wire up actual marketplace APIs
4. **Model Training**: Train on real historical data
5. **Performance Tuning**: Optimize for production workloads
6. **Frontend Integration**: Migrate to React production frontend

## Support

### Documentation

- **Research Analysis**: `COMPREHENSIVE_RESEARCH_ANALYSIS.md`
- **Implementation Guide**: `IMPLEMENTATION_GUIDE.md`
- **System Blueprint**: `SYSTEM_BLUEPRINT.md`

### Code

- **Streamlit App**: `streamlit_app.py`
- **Backend Services**: `backend/app/services/`
- **Enhanced Scraping**: `backend/app/services/enhanced_scraping.py`
- **ML Models**: `backend/app/services/enhanced_ml_models.py`
- **Demand Forecasting**: `backend/app/services/demand_forecasting.py`
- **Dynamic Pricing**: `backend/app/services/dynamic_pricing.py`

## Keyboard Shortcuts

While using the Streamlit app:

- **R**: Rerun the app
- **C**: Clear cache
- **M**: Show/hide menu
- **S**: Show/hide sidebar

## Tips & Tricks

1. **Use Expanders**: Click on expandable sections for detailed information
2. **Refresh Data**: Use the refresh button in the sidebar
3. **Export Results**: Download data from forecast and prediction pages
4. **Monitor Logs**: Check terminal output for detailed logging
5. **Test Scenarios**: Create multiple test cases for validation

---

**Version**: 1.0  
**Last Updated**: October 2025  
**Status**: Ready for Development Testing
