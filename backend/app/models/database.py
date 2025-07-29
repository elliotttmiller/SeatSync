from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, DECIMAL, Text, JSON, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String)
    is_verified = Column(Boolean, default=False)
    subscription_tier = Column(String, default='free')
    stripe_customer_id = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    season_tickets = relationship("SeasonTicket", back_populates="user", cascade="all, delete-orphan")
    marketplace_accounts = relationship("MarketplaceAccount", back_populates="user", cascade="all, delete-orphan")
    automation_rules = relationship("AutomationRule", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

class SeasonTicket(Base):
    __tablename__ = "season_tickets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    team = Column(String, nullable=False, index=True)
    league = Column(String, nullable=False)
    venue = Column(String, nullable=False)
    section = Column(String, nullable=False)
    row = Column(String, nullable=False)
    seat = Column(String, nullable=False)
    season_year = Column(Integer, nullable=False)
    cost_basis = Column(DECIMAL(10, 2))
    total_games = Column(Integer)
    games_remaining = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="season_tickets")
    listings = relationship("Listing", back_populates="season_ticket", cascade="all, delete-orphan")

class MarketplaceAccount(Base):
    __tablename__ = "marketplace_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    platform = Column(String, nullable=False, index=True)  # 'stubhub', 'seatgeek', 'ticketmaster'
    access_token = Column(String, nullable=False)
    refresh_token = Column(String)
    expires_at = Column(DateTime)
    account_id = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="marketplace_accounts")

class Listing(Base):
    __tablename__ = "listings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    season_ticket_id = Column(UUID(as_uuid=True), ForeignKey("season_tickets.id"), nullable=False, index=True)
    game_date = Column(DateTime, nullable=False, index=True)
    platform = Column(String, nullable=False)
    listing_id = Column(String)  # External platform listing ID
    price = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String, default='active', index=True)  # 'active', 'sold', 'cancelled', 'expired'
    original_price = Column(DECIMAL(10, 2))
    final_price = Column(DECIMAL(10, 2))
    sold_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    season_ticket = relationship("SeasonTicket", back_populates="listings")
    ai_predictions = relationship("AIPrediction", back_populates="listing", cascade="all, delete-orphan")

class AIPrediction(Base):
    __tablename__ = "ai_predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=False, index=True)
    model_type = Column(String, nullable=False)  # 'price_prediction', 'sentiment', 'forecast'
    predicted_value = Column(DECIMAL(10, 2))
    confidence_score = Column(DECIMAL(3, 2))
    features = Column(JSONB)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    listing = relationship("Listing", back_populates="ai_predictions")

class AutomationRule(Base):
    __tablename__ = "automation_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    rule_type = Column(String, nullable=False)  # 'pricing', 'listing', 'alert'
    conditions = Column(JSONB, nullable=False)
    actions = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="automation_rules")

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team = Column(String, nullable=False, index=True)
    opponent = Column(String, nullable=False)
    game_date = Column(DateTime, nullable=False, index=True)
    data_type = Column(String, nullable=False)  # 'team_stats', 'player_stats', 'weather', 'events'
    data = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=func.now())

class SentimentData(Base):
    __tablename__ = "sentiment_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team = Column(String, nullable=False, index=True)
    opponent = Column(String, nullable=False)
    game_date = Column(DateTime, nullable=False, index=True)
    sentiment_score = Column(DECIMAL(3, 2))
    sentiment_volume = Column(Integer)
    sources = Column(JSONB)
    created_at = Column(DateTime, default=func.now())

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    device_info = Column(JSONB)
    created_at = Column(DateTime, default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(UUID(as_uuid=True))
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime, default=func.now(), index=True)

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String, nullable=False)  # 'price_alert', 'sale_confirmation', 'market_update'
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSONB)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")

class RateLimit(Base):
    __tablename__ = "rate_limits"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    endpoint = Column(String, nullable=False)
    request_count = Column(Integer, default=1)
    window_start = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

# Pydantic models for API requests/responses
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    is_verified: bool
    subscription_tier: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SeasonTicketCreate(BaseModel):
    team: str
    league: str
    venue: str
    section: str
    row: str
    seat: str
    season_year: int
    cost_basis: Optional[float] = None
    total_games: Optional[int] = None
    games_remaining: Optional[int] = None

class SeasonTicketResponse(BaseModel):
    id: uuid.UUID
    team: str
    league: str
    venue: str
    section: str
    row: str
    seat: str
    season_year: int
    cost_basis: Optional[float]
    total_games: Optional[int]
    games_remaining: Optional[int]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ListingCreate(BaseModel):
    season_ticket_id: uuid.UUID
    game_date: datetime
    platform: str
    price: float

class ListingResponse(BaseModel):
    id: uuid.UUID
    season_ticket_id: uuid.UUID
    game_date: datetime
    platform: str
    listing_id: Optional[str]
    price: float
    status: str
    original_price: Optional[float]
    final_price: Optional[float]
    sold_at: Optional[datetime]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AIPredictionResponse(BaseModel):
    id: uuid.UUID
    listing_id: uuid.UUID
    model_type: str
    predicted_value: Optional[float]
    confidence_score: Optional[float]
    features: Optional[dict]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class AutomationRuleCreate(BaseModel):
    name: str
    rule_type: str
    conditions: dict
    actions: dict

class AutomationRuleResponse(BaseModel):
    id: uuid.UUID
    name: str
    rule_type: str
    conditions: dict
    actions: dict
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True) 