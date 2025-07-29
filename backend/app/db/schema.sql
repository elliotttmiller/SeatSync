-- SeatSync Production Database Schema
-- PostgreSQL + TimescaleDB for time-series data

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    phone VARCHAR,
    is_verified BOOLEAN DEFAULT FALSE,
    subscription_tier VARCHAR DEFAULT 'free',
    stripe_customer_id VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Season Ticket Portfolios
CREATE TABLE season_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    team VARCHAR NOT NULL,
    league VARCHAR NOT NULL,
    venue VARCHAR NOT NULL,
    section VARCHAR NOT NULL,
    row VARCHAR NOT NULL,
    seat VARCHAR NOT NULL,
    season_year INTEGER NOT NULL,
    cost_basis DECIMAL(10,2),
    total_games INTEGER,
    games_remaining INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Marketplace Integrations
CREATE TABLE marketplace_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR NOT NULL, -- 'stubhub', 'seatgeek', 'ticketmaster'
    access_token VARCHAR NOT NULL,
    refresh_token VARCHAR,
    expires_at TIMESTAMP,
    account_id VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Active Listings
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    season_ticket_id UUID REFERENCES season_tickets(id) ON DELETE CASCADE,
    game_date DATE NOT NULL,
    platform VARCHAR NOT NULL,
    listing_id VARCHAR,
    price DECIMAL(10,2) NOT NULL,
    status VARCHAR DEFAULT 'active', -- 'active', 'sold', 'cancelled', 'expired'
    original_price DECIMAL(10,2),
    final_price DECIMAL(10,2),
    sold_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Price History (TimescaleDB Hypertable)
CREATE TABLE price_history (
    time TIMESTAMP NOT NULL,
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    price DECIMAL(10,2) NOT NULL,
    platform VARCHAR NOT NULL,
    views INTEGER DEFAULT 0,
    favorites INTEGER DEFAULT 0
);

-- Enable TimescaleDB hypertable
SELECT create_hypertable('price_history', 'time');

-- AI Model Predictions
CREATE TABLE ai_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    model_type VARCHAR NOT NULL, -- 'price_prediction', 'sentiment', 'forecast'
    predicted_value DECIMAL(10,2),
    confidence_score DECIMAL(3,2),
    features JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Automation Rules
CREATE TABLE automation_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    rule_type VARCHAR NOT NULL, -- 'pricing', 'listing', 'alert'
    conditions JSONB NOT NULL,
    actions JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Market Data
CREATE TABLE market_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team VARCHAR NOT NULL,
    opponent VARCHAR NOT NULL,
    game_date DATE NOT NULL,
    data_type VARCHAR NOT NULL, -- 'team_stats', 'player_stats', 'weather', 'events'
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sentiment Data
CREATE TABLE sentiment_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team VARCHAR NOT NULL,
    opponent VARCHAR NOT NULL,
    game_date DATE NOT NULL,
    sentiment_score DECIMAL(3,2),
    sentiment_volume INTEGER,
    sources JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User Sessions
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    device_info JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit Log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR NOT NULL,
    resource_type VARCHAR NOT NULL,
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR NOT NULL, -- 'price_alert', 'sale_confirmation', 'market_update'
    title VARCHAR NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- API Rate Limiting
CREATE TABLE rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR NOT NULL,
    request_count INTEGER DEFAULT 1,
    window_start TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_season_tickets_user_id ON season_tickets(user_id);
CREATE INDEX idx_season_tickets_team ON season_tickets(team);
CREATE INDEX idx_listings_season_ticket_id ON listings(season_ticket_id);
CREATE INDEX idx_listings_status ON listings(status);
CREATE INDEX idx_listings_game_date ON listings(game_date);
CREATE INDEX idx_marketplace_accounts_user_id ON marketplace_accounts(user_id);
CREATE INDEX idx_marketplace_accounts_platform ON marketplace_accounts(platform);
CREATE INDEX idx_ai_predictions_listing_id ON ai_predictions(listing_id);
CREATE INDEX idx_automation_rules_user_id ON automation_rules(user_id);
CREATE INDEX idx_market_data_team_date ON market_data(team, game_date);
CREATE INDEX idx_sentiment_data_team_date ON sentiment_data(team, game_date);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);

-- Create composite indexes
CREATE INDEX idx_listings_user_status ON listings(season_ticket_id, status);
CREATE INDEX idx_price_history_listing_time ON price_history(listing_id, time DESC);

-- Create TimescaleDB compression policy
SELECT add_compression_policy('price_history', INTERVAL '7 days');

-- Create data retention policy (keep 2 years of price history)
SELECT add_retention_policy('price_history', INTERVAL '2 years');

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_season_tickets_updated_at BEFORE UPDATE ON season_tickets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_listings_updated_at BEFORE UPDATE ON listings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_marketplace_accounts_updated_at BEFORE UPDATE ON marketplace_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_automation_rules_updated_at BEFORE UPDATE ON automation_rules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to calculate portfolio value
CREATE OR REPLACE FUNCTION calculate_portfolio_value(user_uuid UUID)
RETURNS DECIMAL AS $$
DECLARE
    total_value DECIMAL := 0;
BEGIN
    SELECT COALESCE(SUM(
        CASE 
            WHEN l.status = 'sold' THEN l.final_price
            WHEN l.status = 'active' THEN l.price
            ELSE st.cost_basis
        END
    ), 0)
    INTO total_value
    FROM season_tickets st
    LEFT JOIN listings l ON st.id = l.season_ticket_id
    WHERE st.user_id = user_uuid;
    
    RETURN total_value;
END;
$$ LANGUAGE plpgsql;

-- Create function to get portfolio performance
CREATE OR REPLACE FUNCTION get_portfolio_performance(user_uuid UUID)
RETURNS TABLE(
    total_cost DECIMAL,
    total_value DECIMAL,
    total_profit DECIMAL,
    roi_percentage DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(SUM(st.cost_basis), 0) as total_cost,
        calculate_portfolio_value(user_uuid) as total_value,
        calculate_portfolio_value(user_uuid) - COALESCE(SUM(st.cost_basis), 0) as total_profit,
        CASE 
            WHEN COALESCE(SUM(st.cost_basis), 0) > 0 
            THEN ((calculate_portfolio_value(user_uuid) - COALESCE(SUM(st.cost_basis), 0)) / COALESCE(SUM(st.cost_basis), 0)) * 100
            ELSE 0
        END as roi_percentage
    FROM season_tickets st
    WHERE st.user_id = user_uuid;
END;
$$ LANGUAGE plpgsql;

-- Create views for common queries
CREATE VIEW active_listings_view AS
SELECT 
    l.id,
    l.game_date,
    l.platform,
    l.price,
    l.status,
    st.team,
    st.league,
    st.venue,
    st.section,
    st.row,
    st.seat,
    u.email as user_email
FROM listings l
JOIN season_tickets st ON l.season_ticket_id = st.id
JOIN users u ON st.user_id = u.id
WHERE l.status = 'active';

CREATE VIEW portfolio_summary_view AS
SELECT 
    u.id as user_id,
    u.email,
    COUNT(st.id) as total_season_tickets,
    COUNT(l.id) as total_listings,
    COUNT(CASE WHEN l.status = 'active' THEN 1 END) as active_listings,
    COUNT(CASE WHEN l.status = 'sold' THEN 1 END) as sold_listings,
    calculate_portfolio_value(u.id) as portfolio_value
FROM users u
LEFT JOIN season_tickets st ON u.id = st.user_id
LEFT JOIN listings l ON st.id = l.season_ticket_id
GROUP BY u.id, u.email;

-- Grant permissions (adjust as needed for your Railway setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO seatsync_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO seatsync_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO seatsync_user; 