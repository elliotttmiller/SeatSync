# Railway Deployment Guide for SeatSync

## Overview
This guide covers deploying SeatSync to Railway, including both the FastAPI backend and PostgreSQL database.

## Prerequisites
- Railway account (https://railway.app)
- GitHub repository with SeatSync code
- Railway CLI (optional but recommended)

## Step 1: Railway Project Setup

### 1.1 Create Railway Project
1. Go to Railway Dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account
5. Select the SeatSync repository

### 1.2 Add PostgreSQL Database
1. In your Railway project dashboard
2. Click "New Service"
3. Select "Database" → "PostgreSQL"
4. Railway will automatically provide the `DATABASE_URL` environment variable

### 1.3 Add Redis (Optional)
1. Click "New Service"
2. Select "Database" → "Redis"
3. Railway will provide the `REDIS_URL` environment variable

## Step 2: Environment Variables

### 2.1 Required Environment Variables
Set these in your Railway project settings:

```bash
# Security
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database (automatically set by Railway)
DATABASE_URL=postgresql://...

# Redis (if using)
REDIS_URL=redis://...

# Environment
ENVIRONMENT=production
DEBUG=false

# External APIs (add as you integrate them)
STUBHUB_API_KEY=your-stubhub-api-key
STUBHUB_API_SECRET=your-stubhub-secret
SEATGEEK_API_KEY=your-seatgeek-api-key
TICKETMASTER_API_KEY=your-ticketmaster-api-key
SPORTRADAR_API_KEY=your-sportradar-api-key
WEATHER_API_KEY=your-weather-api-key
```

### 2.2 Generate Secure Keys
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 3: Deploy Backend

### 3.1 Configure Service
1. In your Railway project, the backend service should be automatically detected
2. Railway will use the `Dockerfile` in the `backend/` directory
3. Set the root directory to `backend/` in Railway settings

### 3.2 Build Configuration
Railway will automatically:
- Detect Python project
- Install dependencies from `requirements.txt`
- Use the `Dockerfile` for containerization
- Expose port 8000

### 3.3 Custom Domain (Optional)
1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain (e.g., `api.seatsync.com`)
4. Configure DNS records as instructed

## Step 4: Database Setup

### 4.1 Initialize Database
After deployment, you'll need to run database migrations:

```bash
# Connect to Railway PostgreSQL
railway connect

# Run migrations (you'll need to create these)
alembic upgrade head
```

### 4.2 Create Initial Tables
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Season tickets table
CREATE TABLE season_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    team VARCHAR NOT NULL,
    section VARCHAR NOT NULL,
    row VARCHAR NOT NULL,
    seat VARCHAR NOT NULL,
    season_year INTEGER NOT NULL,
    cost_basis DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Listings table
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    season_ticket_id UUID REFERENCES season_tickets(id) ON DELETE CASCADE,
    game_date DATE NOT NULL,
    platform VARCHAR NOT NULL,
    listing_id VARCHAR,
    price DECIMAL(10,2) NOT NULL,
    status VARCHAR DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Price history table (TimescaleDB hypertable)
CREATE TABLE price_history (
    time TIMESTAMP NOT NULL,
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    price DECIMAL(10,2) NOT NULL,
    platform VARCHAR NOT NULL
);

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;
SELECT create_hypertable('price_history', 'time');
```

## Step 5: Frontend Deployment

### 5.1 Deploy Frontend to Railway
1. Create a new service in your Railway project
2. Set the root directory to `frontend/`
3. Railway will automatically detect it as a Node.js project

### 5.2 Frontend Environment Variables
```bash
REACT_APP_API_URL=https://your-backend-service.railway.app
REACT_APP_ENVIRONMENT=production
```

### 5.3 Build Configuration
Railway will automatically:
- Install dependencies from `package.json`
- Run `npm run build`
- Serve the static files

## Step 6: Monitoring and Logs

### 6.1 View Logs
```bash
# View backend logs
railway logs --service backend

# View database logs
railway logs --service postgresql
```

### 6.2 Health Checks
Your API includes health check endpoints:
- `GET /health` - Basic health check
- `GET /api/v1/health` - Detailed health check

### 6.3 Railway Metrics
Railway provides:
- CPU and memory usage
- Request metrics
- Error rates
- Response times

## Step 7: CI/CD Setup

### 7.1 Automatic Deployments
Railway automatically deploys on:
- Push to `main` branch
- Pull request merges
- Manual triggers

### 7.2 Environment-Specific Deployments
```bash
# Deploy to staging
railway up --service backend --environment staging

# Deploy to production
railway up --service backend --environment production
```

## Step 8: Production Considerations

### 8.1 Security
- Use strong, unique secrets
- Enable HTTPS (automatic with Railway)
- Set up proper CORS origins
- Implement rate limiting

### 8.2 Performance
- Enable Redis caching
- Optimize database queries
- Use connection pooling
- Monitor response times

### 8.3 Scaling
- Railway automatically scales based on traffic
- Consider horizontal scaling for high load
- Monitor resource usage

## Step 9: Troubleshooting

### 9.1 Common Issues

**Database Connection Issues**
```bash
# Check database URL
railway variables

# Test connection
railway connect
psql $DATABASE_URL
```

**Build Failures**
```bash
# Check build logs
railway logs --service backend

# Common fixes:
# - Update requirements.txt
# - Check Python version compatibility
# - Verify Dockerfile syntax
```

**Environment Variable Issues**
```bash
# List all variables
railway variables

# Set variable
railway variables set SECRET_KEY=your-key
```

### 9.2 Debug Mode
For development, you can enable debug mode:
```bash
railway variables set DEBUG=true
```

## Step 10: Next Steps

### 10.1 API Integration
1. Set up StubHub API credentials
2. Configure SeatGeek API access
3. Test marketplace integrations
4. Implement webhook handling

### 10.2 Monitoring
1. Set up error tracking (Sentry)
2. Configure uptime monitoring
3. Set up alerting for critical issues
4. Monitor API rate limits

### 10.3 Backup Strategy
1. Enable automatic database backups
2. Set up data export procedures
3. Test restore procedures
4. Document disaster recovery plan

## Railway CLI Commands

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to project
railway link

# Deploy
railway up

# View logs
railway logs

# Connect to database
railway connect

# Open in browser
railway open
```

## Cost Optimization

### Railway Pricing
- **Free Tier**: $5/month credit
- **Pro**: $20/month
- **Team**: $20/month per user

### Optimization Tips
1. Use appropriate instance sizes
2. Monitor resource usage
3. Implement caching to reduce database calls
4. Optimize build times
5. Use Railway's built-in CDN for static assets

---

**Railway makes deployment incredibly simple. The key is proper environment variable management and monitoring your application's performance.** 