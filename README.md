# SeatSync Backend

## Overview
SeatSync is an **advanced AI-driven platform** for ticket price prediction, market analysis, and automated trading strategies. Powered by cutting-edge ML ensemble models, real-time data collection from 11+ sources, and universal AI model support.

## 🚀 Key Features

### 🎯 Core Capabilities
- **AI-Powered Price Prediction** - Ensemble models (XGBoost, LSTM, Transformers, Market Microstructure)
- **Real-Time Data Collection** - 11+ integrated data sources (marketplaces, sports APIs, AI models)
- **Universal AI Support** - OpenAI, Anthropic, Google Gemini, Ollama, HuggingFace
- **Advanced Trading Algorithms** - 5 sophisticated strategies (momentum, mean reversion, arbitrage, market making, portfolio optimization)
- **Comprehensive Feature Engineering** - 50+ features across 6 categories
- **Market Intelligence** - Real-time sentiment analysis and regime detection

### 🎟️ Marketplace Integrations
- **StubHub API** - Real-time ticket inventory and pricing
- **SeatGeek API** - Event discovery and price statistics
- **Ticketmaster API** - Official event data and pricing
- **VividSeats** - (Placeholder for browser automation)

### 🏀 Sports Data Sources
- **ESPN API** - Multi-sport scores and schedules (FREE)
- **BallDontLie** - NBA statistics (FREE)
- **MLB Stats API** - Official MLB data (FREE)
- **TheSportsDB** - NFL and multi-sport data (FREE)
- **Sportradar** - Premium professional data (PAID)

### 🤖 AI Model Support
- **OpenAI** (GPT-4, GPT-3.5)
- **Anthropic** (Claude 3 Opus, Sonnet)
- **Google Gemini** (Gemini Pro)
- **Ollama** (Local LLMs - llama2, mistral, etc.)
- **HuggingFace** (Thousands of open models)

## Setup
## Setup

### Quick Start (Minimal Configuration)
Works with **FREE** APIs out of the box!

1. Clone the repo and install dependencies:
   ```sh
   pip install -r backend/requirements.txt
   ```

2. Copy test environment file:
   ```sh
   cp backend/.env.test backend/.env
   ```

3. Run database migrations:
   ```sh
   alembic upgrade head
   ```

4. Start the backend:
   ```sh
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Configuration

#### Required Environment Variables (Minimal)
```bash
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
DATABASE_URL=sqlite+aiosqlite:///./seatsync.db
GOOGLE_PROJECT_ID=test_project
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GEMINI_API_KEY=your_gemini_key  # Optional
CORS_ORIGIN=http://localhost:3000
```

#### Optional API Keys (For Enhanced Features)

**Marketplace APIs**:
```bash
STUBHUB_API_KEY=your_key
SEATGEEK_CLIENT_ID=your_id
SEATGEEK_CLIENT_SECRET=your_secret
TICKETMASTER_API_KEY=your_key
```

**AI Models**:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
OLLAMA_ENDPOINT=http://localhost:11434
HUGGINGFACE_API_KEY=hf_...
```

**Sports Data** (Most have FREE tiers):
```bash
SPORTRADAR_API_KEY=your_key  # Premium
BALLDONTLIE_API_KEY=your_key  # Optional (higher limits)
THESPORTSDB_API_KEY=3  # Free tier
```

See [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md) for detailed setup instructions.

## Architecture

### Service Layer
```
app/services/
├── ai_service.py              # Central AI orchestration
├── universal_ai_loader.py     # Multi-provider AI support
├── data_ingestion.py          # Real-time data pipeline
├── feature_engineering.py     # 50+ feature extraction
├── ensemble_models.py         # ML model ensemble
├── trading_algorithms.py      # Advanced strategies
└── automation_service.py      # Automated workflows
```

### API Endpoints

#### Core Prediction
- `GET /health` - Health check
- `POST /api/v1/predict-price` - AI-powered price prediction
- `POST /api/v1/smart-pricing-recommendation` - Pricing strategies
- `GET /api/v1/market-sentiment/{team}` - Sentiment analysis

#### Advanced Intelligence
- `POST /api/v1/intelligence/predict-advanced` - Ensemble predictions
- `POST /api/v1/intelligence/trading-strategy` - Execute strategies
- `POST /api/v1/intelligence/portfolio-optimization` - Optimize portfolio
- `POST /api/v1/intelligence/data-pipeline/start` - Start data collection
- `POST /api/v1/intelligence/models/train` - Train ML models
- `GET /api/v1/intelligence/market-intelligence` - Market analysis

#### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Refresh token

#### Automation
- `POST /api/v1/automation/rules` - Create automation rules
- `GET /api/v1/automation/rules` - List rules
- `POST /api/v1/automation/execute/{rule_id}` - Execute rule

## Testing
Run all tests:
```sh
pytest -v -s
```

Run specific test suites:
```sh
# Health check tests
pytest backend/tests/test_health.py -v

# Advanced AI tests
pytest backend/tests/test_advanced_ai.py -v

# API endpoint tests
pytest backend/tests/test_endpoints.py -v
```

## Performance Metrics

### Data Collection
- **Sub-second predictions** with ensemble models
- **Real-time processing** with 30-second intervals
- **Parallel collection** from all sources
- **10,000+ predictions/second** scalability

### Model Performance
- **XGBoost**: Gradient boosting with hyperparameter optimization
- **LSTM**: Sequence-to-sequence for time series
- **Transformer**: Multi-head attention for context
- **Market Microstructure**: Custom model for dynamics

## Deployment

### Development
```sh
uvicorn app.main:app --reload
```

### Production (Railway/GCP)
```sh
# Railway
railway up

# Docker
docker build -t seatsync-backend .
docker run -p 8000:8000 seatsync-backend

# GCP Cloud Run
gcloud run deploy seatsync-backend \
  --source . \
  --platform managed \
  --region us-central1
```

## Documentation

- **[API Integration Guide](API_INTEGRATION_GUIDE.md)** - Complete API setup guide
- **[Marketplace Integration](MARKETPLACE_INTEGRATION.md)** - Ticket marketplace APIs
- **[Advanced AI Implementation](ADVANCED_AI_IMPLEMENTATION.md)** - ML/AI architecture

## Key Technologies

- **FastAPI** - Modern async web framework
- **SQLAlchemy 2.0** - Database ORM
- **Pydantic** - Data validation
- **PyTorch** - Deep learning (LSTM, Transformers)
- **XGBoost** - Gradient boosting
- **SciPy** - Portfolio optimization
- **httpx/aiohttp** - Async HTTP clients

## Cloud Function
- Summarizes news/social context and stores in BigQuery.
- Deploy and schedule with GCP Cloud Functions and Scheduler.

## Contributing
PRs welcome! See issues for roadmap and bugs.

## License
MIT

---

**Built with ❤️ for the sports ticket trading community** 