# Hybrid AI Strategy for SeatSync

## Overview

This document outlines our hybrid approach to AI/ML implementation, leveraging Railway's strengths while using specialized platforms for model training.

## Strategy Summary

### Training (Offline) → Inference (Railway)
- **Training**: Google Colab Pro / AWS SageMaker (GPU-powered)
- **Deployment**: Railway (CPU-optimized for inference)
- **Storage**: Railway PostgreSQL + S3 for model artifacts

## Phase 1: Model Training Infrastructure

### 1.1 Google Colab Pro Setup
```python
# Training Environment (Colab Pro - $10/month)
# Advantages: GPU access, 100GB storage, 24hr runtime

# Install required packages
!pip install xgboost scikit-learn pandas numpy
!pip install prophet spacy transformers
!pip install psycopg2-binary redis

# Connect to Railway PostgreSQL
import psycopg2
from railway import Railway

# Fetch training data
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
query = """
SELECT * FROM price_history 
WHERE time > NOW() - INTERVAL '1 year'
ORDER BY time;
"""
training_data = pd.read_sql(query, conn)
```

### 1.2 AWS SageMaker Alternative
```python
# For larger models or more complex training
# SageMaker Notebook Instance (ml.t3.large - $0.083/hour)

import sagemaker
from sagemaker import get_execution_role

# Initialize SageMaker session
sagemaker_session = sagemaker.Session()
role = get_execution_role()

# Training script
training_script = """
import xgboost as xgb
import joblib
import pandas as pd

# Load data from Railway
# Train model
# Save model artifact
model = xgb.XGBRegressor()
model.fit(X_train, y_train)
joblib.dump(model, '/opt/ml/model/price_predictor.pkl')
"""
```

## Phase 2: Model Architecture

### 2.1 Lightweight Models (Railway-Optimized)

#### Price Prediction Model
```python
# backend/app/ml/models/price_predictor.py
import joblib
import xgboost as xgb
from typing import Dict, List
import numpy as np

class PricePredictor:
    def __init__(self):
        self.model = None
        self.feature_names = [
            'days_until_game', 'team_rank', 'opponent_rank',
            'day_of_week', 'is_rivalry', 'is_playoff',
            'weather_score', 'sentiment_score', 'historical_avg'
        ]
    
    def load_model(self, model_path: str):
        """Load trained model from file"""
        self.model = joblib.load(model_path)
    
    def predict(self, features: Dict) -> Dict:
        """Make price prediction with confidence interval"""
        # Feature engineering
        X = self._engineer_features(features)
        
        # Make prediction
        prediction = self.model.predict(X)[0]
        
        # Calculate confidence (simplified)
        confidence = 0.85  # Would be calculated from model uncertainty
        
        return {
            'predicted_price': float(prediction),
            'confidence': confidence,
            'price_range': {
                'low': prediction * 0.9,
                'high': prediction * 1.1
            }
        }
    
    def _engineer_features(self, features: Dict) -> np.ndarray:
        """Convert raw features to model input"""
        # Feature engineering logic
        return np.array([features.get(f, 0) for f in self.feature_names]).reshape(1, -1)
```

#### Sentiment Analysis Model
```python
# backend/app/ml/models/sentiment_analyzer.py
import spacy
from textblob import TextBlob
from typing import Dict, List

class SentimentAnalyzer:
    def __init__(self):
        # Load spaCy model (lightweight)
        self.nlp = spacy.load("en_core_web_sm")
    
    def analyze_sentiment(self, texts: List[str]) -> Dict:
        """Analyze sentiment of multiple texts"""
        sentiments = []
        
        for text in texts:
            # Use TextBlob for sentiment (faster than BERT)
            blob = TextBlob(text)
            sentiment_score = blob.sentiment.polarity
            
            # Additional spaCy analysis
            doc = self.nlp(text)
            
            # Extract key entities
            entities = [ent.text for ent in doc.ents if ent.label_ in ['PERSON', 'ORG']]
            
            sentiments.append({
                'text': text,
                'sentiment_score': sentiment_score,
                'entities': entities,
                'confidence': abs(blob.sentiment.subjectivity)
            })
        
        # Aggregate sentiment
        avg_sentiment = sum(s['sentiment_score'] for s in sentiments) / len(sentiments)
        
        return {
            'overall_sentiment': avg_sentiment,
            'individual_sentiments': sentiments,
            'confidence': sum(s['confidence'] for s in sentiments) / len(sentiments)
        }
```

### 2.2 Time-Series Forecasting
```python
# backend/app/ml/models/price_forecaster.py
from prophet import Prophet
import pandas as pd
from typing import Dict, List

class PriceForecaster:
    def __init__(self):
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative'
        )
    
    def train(self, historical_data: pd.DataFrame):
        """Train Prophet model on historical price data"""
        # Prepare data for Prophet
        df = historical_data.rename(columns={
            'time': 'ds',
            'price': 'y'
        })
        
        # Add custom seasonality for sports events
        self.model.add_seasonality(
            name='sports_season',
            period=365.25,
            fourier_order=10
        )
        
        self.model.fit(df)
    
    def forecast(self, periods: int = 30) -> Dict:
        """Generate price forecast"""
        future = self.model.make_future_dataframe(periods=periods)
        forecast = self.model.predict(future)
        
        return {
            'forecast': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods),
            'trend': forecast[['ds', 'trend']].tail(periods),
            'seasonality': forecast[['ds', 'yearly', 'weekly']].tail(periods)
        }
```

## Phase 3: Railway Integration

### 3.1 Model Loading Service
```python
# backend/app/ml/model_service.py
import os
import joblib
from typing import Dict, Optional
from .models.price_predictor import PricePredictor
from .models.sentiment_analyzer import SentimentAnalyzer
from .models.price_forecaster import PriceForecaster

class ModelService:
    def __init__(self):
        self.price_predictor = None
        self.sentiment_analyzer = None
        self.price_forecaster = None
        self.models_loaded = False
    
    async def load_models(self):
        """Load all ML models at startup"""
        try:
            # Load price prediction model
            model_path = os.getenv('MODEL_PATH', '/app/models/')
            self.price_predictor = PricePredictor()
            self.price_predictor.load_model(f"{model_path}/price_predictor.pkl")
            
            # Initialize sentiment analyzer
            self.sentiment_analyzer = SentimentAnalyzer()
            
            # Initialize price forecaster
            self.price_forecaster = PriceForecaster()
            
            self.models_loaded = True
            print("✅ All ML models loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            self.models_loaded = False
    
    async def get_price_prediction(self, features: Dict) -> Dict:
        """Get price prediction for a ticket"""
        if not self.models_loaded:
            return {"error": "Models not loaded"}
        
        return self.price_predictor.predict(features)
    
    async def analyze_market_sentiment(self, texts: List[str]) -> Dict:
        """Analyze market sentiment"""
        if not self.models_loaded:
            return {"error": "Models not loaded"}
        
        return self.sentiment_analyzer.analyze_sentiment(texts)
    
    async def forecast_price_trajectory(self, historical_data: pd.DataFrame) -> Dict:
        """Forecast price trajectory"""
        if not self.models_loaded:
            return {"error": "Models not loaded"}
        
        self.price_forecaster.train(historical_data)
        return self.price_forecaster.forecast()
```

### 3.2 Railway Startup Configuration
```python
# backend/app/main.py
from fastapi import FastAPI
from app.ml.model_service import ModelService
import asyncio

app = FastAPI()
model_service = ModelService()

@app.on_event("startup")
async def startup_event():
    """Load ML models on application startup"""
    await model_service.load_models()

@app.get("/api/v1/ml/health")
async def ml_health_check():
    """Check ML model status"""
    return {
        "models_loaded": model_service.models_loaded,
        "available_models": [
            "price_predictor",
            "sentiment_analyzer", 
            "price_forecaster"
        ]
    }
```

## Phase 4: Training Pipeline

### 4.1 Automated Training Script
```python
# scripts/train_models.py
import os
import sys
import pandas as pd
import psycopg2
import joblib
from datetime import datetime, timedelta
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

def fetch_training_data():
    """Fetch training data from Railway PostgreSQL"""
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    
    query = """
    SELECT 
        ph.time,
        ph.price,
        ph.platform,
        st.team,
        st.section,
        st.row,
        st.seat,
        EXTRACT(EPOCH FROM (l.game_date - ph.time))/86400 as days_until_game,
        EXTRACT(DOW FROM l.game_date) as day_of_week
    FROM price_history ph
    JOIN listings l ON ph.listing_id = l.id
    JOIN season_tickets st ON l.season_ticket_id = st.id
    WHERE ph.time > NOW() - INTERVAL '1 year'
    ORDER BY ph.time;
    """
    
    return pd.read_sql(query, conn)

def train_price_predictor(data: pd.DataFrame):
    """Train XGBoost price prediction model"""
    # Feature engineering
    features = [
        'days_until_game', 'day_of_week', 'price'
    ]
    
    X = data[features].dropna()
    y = X.pop('price')
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Price Predictor Performance:")
    print(f"MAE: ${mae:.2f}")
    print(f"R²: {r2:.3f}")
    
    # Save model
    joblib.dump(model, 'models/price_predictor.pkl')
    
    return model

def main():
    """Main training pipeline"""
    print("🚀 Starting model training pipeline...")
    
    # Fetch data
    print("📊 Fetching training data...")
    data = fetch_training_data()
    print(f"📈 Loaded {len(data)} records")
    
    # Train models
    print("🤖 Training price prediction model...")
    price_model = train_price_predictor(data)
    
    # Save training metadata
    metadata = {
        'training_date': datetime.now().isoformat(),
        'data_points': len(data),
        'model_version': '1.0.0'
    }
    
    joblib.dump(metadata, 'models/training_metadata.pkl')
    
    print("✅ Training pipeline completed!")

if __name__ == "__main__":
    main()
```

### 4.2 Railway Model Deployment
```bash
# Deploy trained models to Railway
# 1. Train models locally or in Colab
python scripts/train_models.py

# 2. Upload models to Railway
railway up --service backend

# 3. Models are automatically loaded on startup
```

## Phase 5: Performance Optimization

### 5.1 Caching Strategy
```python
# backend/app/ml/cache_service.py
import redis
import json
from typing import Any, Optional

class MLCacheService:
    def __init__(self):
        self.redis_client = redis.from_url(os.getenv('REDIS_URL'))
        self.cache_ttl = 3600  # 1 hour
    
    async def get_cached_prediction(self, cache_key: str) -> Optional[Dict]:
        """Get cached prediction result"""
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        return None
    
    async def cache_prediction(self, cache_key: str, prediction: Dict):
        """Cache prediction result"""
        self.redis_client.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(prediction)
        )
    
    def generate_cache_key(self, features: Dict) -> str:
        """Generate cache key from features"""
        # Create deterministic key from features
        feature_str = json.dumps(features, sort_keys=True)
        return f"prediction:{hash(feature_str)}"
```

### 5.2 Railway Resource Configuration
```json
// railway.json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  },
  "resources": {
    "memory": "4GB",
    "cpu": "2",
    "storage": "10GB"
  }
}
```

## Cost Analysis

### Training Costs
- **Google Colab Pro**: $10/month
- **AWS SageMaker** (occasional): $50-100/month
- **Total Training**: $60-110/month

### Inference Costs (Railway)
- **Development**: $5-10/month
- **Production**: $50-100/month
- **Total Inference**: $55-110/month

### Total AI/ML Costs
- **MVP Phase**: $65-120/month
- **Growth Phase**: $110-220/month
- **Scale Phase**: $200-400/month

## Success Metrics

### Model Performance
- **Price Prediction Accuracy**: MAE < $20
- **Sentiment Analysis**: 85%+ accuracy
- **Forecast Reliability**: 80%+ within confidence intervals

### System Performance
- **Inference Latency**: < 500ms
- **Model Loading Time**: < 30 seconds
- **Cache Hit Rate**: > 80%

### Business Impact
- **Revenue Increase**: 15%+ from optimized pricing
- **User Satisfaction**: 4.5+ star rating for AI features
- **Market Differentiation**: Unique AI capabilities

---

**This hybrid approach gives us the best of both worlds: powerful GPU training when needed, and cost-effective, scalable inference on Railway.** 