# SeatSync Complete API Integration Guide

## Overview

SeatSync integrates with **11+ external data sources** to provide comprehensive ticket price prediction and market analysis. This guide covers all API configurations and usage patterns.

---

## 🎯 Quick Start

### Minimal Configuration (Free Tier)

```bash
# .env file - Works without any paid API keys!
# Optional AI models (if you have keys)
OPENAI_API_KEY=optional
ANTHROPIC_API_KEY=optional
GEMINI_API_KEY=optional

# Optional marketplace APIs (recommended for production)
STUBHUB_API_KEY=optional
SEATGEEK_CLIENT_ID=optional
TICKETMASTER_API_KEY=optional

# Sports APIs (all have free tiers!)
# No configuration needed - works out of the box
```

**What works with zero configuration:**
- ✅ ESPN sports data (completely free)
- ✅ NBA data via BallDontLie (free)
- ✅ NFL data via TheSportsDB (free)
- ✅ MLB official stats API (free)
- ✅ AI prediction models (without AI text generation)

---

## 🎟️ Marketplace APIs (Ticket Price Data)

### 1. StubHub API

**Documentation**: https://developer.stubhub.com/

**Configuration**:
```bash
STUBHUB_API_KEY=your_api_key_here
```

**Sign Up**:
1. Go to https://developer.stubhub.com/
2. Create developer account
3. Register application
4. Get API key from dashboard

**Features**:
- Real-time ticket inventory
- Event discovery
- Section/row/seat level pricing
- Multiple delivery types
- Historical pricing data

**Rate Limits**: ~40 requests/minute

**Cost**: Contact StubHub for pricing

---

### 2. SeatGeek API

**Documentation**: https://platform.seatgeek.com/

**Configuration**:
```bash
SEATGEEK_CLIENT_ID=your_client_id
SEATGEEK_CLIENT_SECRET=your_client_secret
```

**Sign Up**:
1. Visit https://platform.seatgeek.com/
2. Create account
3. Register application
4. Get Client ID & Secret

**Features**:
- Comprehensive event search
- Price statistics (min/max/avg/median)
- Popularity scores
- Venue information
- Real-time updates

**Rate Limits**: 5,000 requests/day (free tier)

**Cost**: Free tier available, paid tiers for higher limits

---

### 3. Ticketmaster API

**Documentation**: https://developer.ticketmaster.com/

**Configuration**:
```bash
TICKETMASTER_API_KEY=your_api_key
```

**Sign Up**:
1. Go to https://developer.ticketmaster.com/
2. Register account
3. Create application
4. Copy Consumer Key as API key

**Features**:
- Event discovery
- Price ranges
- Venue details
- Event classifications
- Sales period info

**Rate Limits**: 5,000 requests/day

**Cost**: Free tier available

---

### 4. Vivid Seats

**Status**: ⚠️ Placeholder (No Public API)

**Configuration**:
```bash
ENABLE_VIVIDSEATS_SCRAPING=true
```

**Note**: Requires browser automation implementation
- Needs Playwright or Selenium
- JavaScript rendering required
- Consider legal/ToS implications

---

## 🏀 Sports Data APIs

### 1. ESPN API (FREE)

**Documentation**: https://gist.github.com/nntrn/ee26cb2a0716de0947a0a4e9a157bc1c

**Configuration**: None required (public API)

**Features**:
- NBA, NFL, MLB, NHL scores
- Team information
- Game schedules
- Real-time updates
- Season information

**Rate Limits**: Generous (public API)

**Cost**: FREE ✅

**Usage**:
```python
from app.services.data_ingestion import ESPNAPI

espn = ESPNAPI()
data = await espn.get_current_data()

print(f"NBA games today: {len(data['data']['nba']['events'])}")
```

---

### 2. BallDontLie API (NBA) (FREE)

**Documentation**: https://www.balldontlie.io/

**Configuration**: Optional API key for higher limits
```bash
BALLDONTLIE_API_KEY=optional_for_higher_limits
```

**Sign Up**: https://www.balldontlie.io/

**Features**:
- NBA games data
- Player statistics
- Team information
- Season stats
- Detailed game data

**Rate Limits**: 60 requests/minute (free), higher with key

**Cost**: FREE ✅ (Pro tier available)

---

### 3. MLB Stats API (FREE)

**Documentation**: https://statsapi.mlb.com/docs/

**Configuration**: None required (official MLB API)

**Features**:
- Game schedules
- Live game data
- Team rosters
- Player statistics
- Historical data

**Rate Limits**: Generous

**Cost**: FREE ✅

---

### 4. TheSportsDB API (NFL/Multi-Sport) (FREE)

**Documentation**: https://www.thesportsdb.com/api.php

**Configuration**:
```bash
THESPORTSDB_API_KEY=3  # Free tier key
```

**Sign Up**: https://www.thesportsdb.com/

**Features**:
- Multi-sport coverage
- Event schedules
- Team information
- League data
- Historical data

**Rate Limits**: Moderate (free tier)

**Cost**: FREE ✅ (Patreon supporters get faster limits)

---

### 5. Sportradar API (Premium)

**Documentation**: https://developer.sportradar.com/

**Configuration**:
```bash
SPORTRADAR_API_KEY=your_api_key
```

**Sign Up**: https://developer.sportradar.com/

**Features**:
- Professional-grade data
- Real-time updates
- Advanced statistics
- Multiple sports
- High reliability

**Rate Limits**: Varies by plan

**Cost**: Contact for pricing (premium service)

---

## 🤖 AI Model APIs

### 1. OpenAI (GPT-4, GPT-3.5)

**Documentation**: https://platform.openai.com/docs

**Configuration**:
```bash
OPENAI_API_KEY=sk-...
```

**Sign Up**: https://platform.openai.com/

**Features**:
- GPT-4 for complex analysis
- GPT-3.5-turbo for fast responses
- Chat completions
- Text generation

**Cost**: Pay-per-token ($0.03/1K tokens for GPT-4)

---

### 2. Anthropic Claude

**Documentation**: https://docs.anthropic.com/

**Configuration**:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

**Sign Up**: https://console.anthropic.com/

**Features**:
- Claude 3 Opus (most capable)
- Claude 3 Sonnet (balanced)
- Long context windows
- Detailed reasoning

**Cost**: Pay-per-token ($15/million tokens for Opus)

---

### 3. Google Gemini

**Documentation**: https://ai.google.dev/docs

**Configuration**:
```bash
GEMINI_API_KEY=...
```

**Sign Up**: https://makersuite.google.com/

**Features**:
- Gemini Pro
- Multimodal capabilities
- Good for analysis
- Fast responses

**Cost**: Free tier available, paid tiers for production

---

### 4. Ollama (Local Models)

**Documentation**: https://ollama.ai/

**Configuration**:
```bash
OLLAMA_ENDPOINT=http://localhost:11434
OLLAMA_MODEL=llama2
```

**Setup**:
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Start server
ollama serve
```

**Features**:
- Run models locally
- No API costs
- Privacy (data stays local)
- Various model sizes

**Cost**: FREE ✅ (hardware costs only)

---

### 5. HuggingFace

**Documentation**: https://huggingface.co/docs/api-inference

**Configuration**:
```bash
HUGGINGFACE_API_KEY=hf_...
HUGGINGFACE_MODEL=meta-llama/Llama-2-70b-chat-hf
```

**Sign Up**: https://huggingface.co/

**Features**:
- Access to thousands of models
- Inference API
- Model hosting
- Community models

**Cost**: Free tier available, Pro for faster inference

---

## 🌤️ External Context APIs (Future)

### Weather API (Planned)

**Recommended**: OpenWeatherMap

**Configuration**:
```bash
OPENWEATHERMAP_API_KEY=your_key
```

**Use Case**: Weather impact on ticket demand

---

### News API (Planned)

**Recommended**: NewsAPI.org

**Configuration**:
```bash
NEWS_API_KEY=your_key
```

**Use Case**: Sentiment analysis from news

---

### Social Media (Planned)

**Twitter API** (X):
```bash
TWITTER_BEARER_TOKEN=your_token
```

**Reddit API**:
```bash
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
```

**Use Case**: Social sentiment analysis

---

## 📊 Usage Patterns

### Basic Data Collection

```python
from app.services.data_ingestion import AdvancedDataPipeline
from app.db.session import get_db

async def collect_all_data():
    pipeline = AdvancedDataPipeline()
    db = await get_db()
    
    # Collect from all sources in parallel
    async for data in pipeline.real_time_data_stream(db):
        print(f"Data type: {data['type']}")
        print(f"Status: {data['status']}")
        
        if data['type'] == 'marketplace':
            # Process ticket listings
            pass
        elif data['type'] == 'sports':
            # Process sports data
            pass
```

### AI Text Generation

```python
from app.services.universal_ai_loader import get_universal_loader

async def generate_analysis(prompt: str):
    loader = get_universal_loader()
    
    # Automatically uses best available model
    result = await loader.generate_text(
        prompt=prompt,
        max_tokens=500,
        temperature=0.7
    )
    
    print(f"Used: {result['provider']}:{result['model_used']}")
    print(f"Response: {result['text']}")
```

### Price Prediction with AI

```python
from app.services.ai_service import AIService

async def predict_price(ticket_data: dict, db):
    ai_service = AIService()
    
    # Uses ensemble models + AI insights
    prediction = await ai_service.predict_ticket_price(
        ticket_data=ticket_data,
        db=db,
        include_context=True,
        use_ensemble=True
    )
    
    print(f"Predicted price: ${prediction['predicted_price']}")
    print(f"Confidence: {prediction['confidence']:.1%}")
```

---

## 🔒 Security Best Practices

### API Key Management

```bash
# Never commit .env files
echo ".env" >> .gitignore
echo "*.env" >> .gitignore

# Use different keys for dev/staging/prod
.env.development
.env.staging
.env.production
```

### Environment Variables in Production

```bash
# Railway/Heroku
railway variables set OPENAI_API_KEY=sk-...

# Docker
docker run -e OPENAI_API_KEY=sk-... ...

# Kubernetes
kubectl create secret generic api-keys \
  --from-literal=OPENAI_API_KEY=sk-...
```

---

## 💰 Cost Estimation

### Minimal Configuration (FREE)
- ESPN: FREE
- NBA (BallDontLie): FREE
- NFL (TheSportsDB): FREE
- MLB: FREE
- No AI models: $0/month
- **Total: $0/month** ✅

### Standard Configuration
- Above FREE services
- Gemini AI: ~$10/month
- SeatGeek API: FREE tier
- **Total: ~$10/month**

### Production Configuration
- All marketplace APIs: ~$100-300/month
- OpenAI GPT-4: ~$50-200/month
- Sportradar: ~$500+/month
- **Total: ~$650-800/month**

### Enterprise Configuration
- Premium tier all services: ~$2000+/month
- Dedicated support
- Higher rate limits
- Custom integrations

---

## 🚀 Getting Started Checklist

### Minimum Viable Setup (5 minutes)
- [ ] Clone repository
- [ ] Copy `.env.test` to `.env`
- [ ] Run `pip install -r requirements.txt`
- [ ] Run `pytest` (should pass)
- [ ] Start server: `uvicorn app.main:app`
- ✅ Working with free APIs!

### Add Marketplace Data (30 minutes)
- [ ] Sign up for SeatGeek (free tier)
- [ ] Get Client ID & Secret
- [ ] Add to `.env`
- [ ] Test: Run data collection endpoint
- ✅ Real ticket price data!

### Add AI Analysis (15 minutes)
- [ ] Get Gemini API key (free tier)
- [ ] Add to `.env`
- [ ] Test: Call prediction endpoint
- ✅ AI-powered predictions!

---

## 📚 Additional Resources

### Official Documentations
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Pydantic Docs](https://docs.pydantic.dev/)

### Community Resources
- [SeatSync GitHub Issues](https://github.com/elliotttmiller/SeatSync/issues)
- [FastAPI Discord](https://discord.gg/fastapi)

### Learning Resources
- [API Integration Best Practices](https://docs.github.com/en/rest/guides/best-practices-for-integrators)
- [Rate Limiting Strategies](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)

---

## 🆘 Support

### Troubleshooting

**Issue**: API returns 401 Unauthorized
- Check API key is correct
- Verify key hasn't expired
- Check API key has necessary permissions

**Issue**: API returns 429 Too Many Requests
- Implement rate limiting
- Add exponential backoff
- Consider upgrading tier

**Issue**: No data returned
- Check API is operational
- Verify network connectivity
- Check request parameters

### Contact

- GitHub Issues: https://github.com/elliotttmiller/SeatSync/issues
- Email: dev@seatsync.com

---

**Last Updated**: 2024-01-20  
**Version**: 2.0.0
