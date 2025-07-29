# SeatSync Development Project Structure

## Project Overview
SeatSync - AI-Powered Sports Ticket Portfolio Management Platform

## Phase 0: Foundation Setup (Weeks 1-2)

### 1. Development Environment Setup
```
SeatSync/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration, security
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── ml/             # Machine learning models
│   │   └── utils/          # Helper functions
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API calls
│   │   ├── hooks/          # Custom React hooks
│   │   ├── types/          # TypeScript types
│   │   └── utils/          # Helper functions
│   ├── public/             # Static assets
│   ├── package.json
│   └── Dockerfile
├── infrastructure/         # Docker, Kubernetes configs
│   ├── docker-compose.yml
│   ├── k8s/               # Kubernetes manifests
│   └── scripts/           # Deployment scripts
├── docs/                  # Documentation
└── README.md
```

### 2. Technology Stack Confirmation
- **Backend**: FastAPI + Python 3.11+
- **Frontend**: React 18 + TypeScript
- **Database**: PostgreSQL + TimescaleDB
- **Cache**: Redis
- **Infrastructure**: Docker + Kubernetes
- **Cloud**: AWS (EC2, RDS, S3, Lambda)

### 3. Initial Development Tasks

#### Week 1: Backend Foundation
- [ ] Set up FastAPI project structure
- [ ] Configure PostgreSQL + TimescaleDB
- [ ] Implement user authentication (JWT)
- [ ] Create basic API endpoints
- [ ] Set up Docker development environment

#### Week 2: Frontend Foundation
- [ ] Set up React + TypeScript project
- [ ] Configure Material-UI or Ant Design
- [ ] Implement authentication UI
- [ ] Create basic dashboard layout
- [ ] Set up API integration layer

### 4. MVP Feature Priority (Phase 1)
1. **User Authentication** (Week 3)
2. **Marketplace Account Integration** (Week 4-5)
3. **Manual Listing Engine** (Week 6)
4. **Sync Engine** (Week 7-8)
5. **Basic Dashboard** (Week 9)
6. **Basic Price Suggestion** (Week 10)

### 5. Development Workflow
- **Git Flow**: Feature branches → Develop → Main
- **CI/CD**: GitHub Actions for automated testing
- **Code Quality**: Pre-commit hooks, linting, type checking
- **Testing**: Unit tests for backend, integration tests for API

### 6. API Integration Strategy
- **Priority 1**: StubHub API (most comprehensive)
- **Priority 2**: SeatGeek API
- **Priority 3**: Ticketmaster API
- **Fallback**: Web scraping for platforms without APIs

### 7. Database Schema (Initial)
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Season tickets table
CREATE TABLE season_tickets (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    team VARCHAR NOT NULL,
    section VARCHAR NOT NULL,
    row VARCHAR NOT NULL,
    seat VARCHAR NOT NULL,
    season_year INTEGER NOT NULL,
    cost_basis DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Listings table
CREATE TABLE listings (
    id UUID PRIMARY KEY,
    season_ticket_id UUID REFERENCES season_tickets(id),
    game_date DATE NOT NULL,
    platform VARCHAR NOT NULL, -- 'stubhub', 'seatgeek', etc.
    listing_id VARCHAR, -- External platform listing ID
    price DECIMAL(10,2) NOT NULL,
    status VARCHAR DEFAULT 'active', -- 'active', 'sold', 'cancelled'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Price history table (TimescaleDB hypertable)
CREATE TABLE price_history (
    time TIMESTAMP NOT NULL,
    listing_id UUID REFERENCES listings(id),
    price DECIMAL(10,2) NOT NULL,
    platform VARCHAR NOT NULL
);
SELECT create_hypertable('price_history', 'time');
```

### 8. Next Steps
1. **Set up development environment**
2. **Create project repository**
3. **Implement basic authentication**
4. **Design database schema**
5. **Start API integration research** 