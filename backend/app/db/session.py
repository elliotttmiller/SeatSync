from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database engine with Railway optimizations
def create_database_engine():
    """Create database engine optimized for Railway deployment"""
    
    # Parse Railway DATABASE_URL
    database_url = settings.DATABASE_URL
    
    # Engine configuration for production
    engine_config = {
        "poolclass": QueuePool,
        "pool_size": 10,  # Number of connections to maintain
        "max_overflow": 20,  # Additional connections when pool is full
        "pool_pre_ping": True,  # Verify connections before use
        "pool_recycle": 3600,  # Recycle connections after 1 hour
        "echo": settings.DEBUG,  # Log SQL queries in debug mode
    }
    
    try:
        engine = create_engine(
            database_url,
            **engine_config
        )
        
        # Test connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
                       logger.info("Database connection established successfully")
        return engine
        
    except Exception as e:
                       logger.error(f"Database connection failed: {e}")
        raise

# Create engine instance
engine = create_database_engine()

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from app.models.database import Base
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
                       logger.info("Database tables created successfully")
        
        # Verify TimescaleDB extension
        with engine.connect() as conn:
            result = conn.execute("SELECT * FROM pg_extension WHERE extname = 'timescaledb'")
            if result.fetchone():
                                   logger.info("TimescaleDB extension is active")
            else:
                                   logger.warning("TimescaleDB extension not found")
                
    except Exception as e:
                       logger.error(f"Database initialization failed: {e}")
        raise

def check_db_health() -> bool:
    """Check database health"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
                       logger.error(f"Database health check failed: {e}")
        return False

def get_db_stats():
    """Get database statistics"""
    try:
        with engine.connect() as conn:
            # Get table sizes
            result = conn.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
            """)
            
            table_sizes = result.fetchall()
            
            # Get connection info
            result = conn.execute("""
                SELECT 
                    count(*) as active_connections,
                    count(*) FILTER (WHERE state = 'active') as active_queries
                FROM pg_stat_activity 
                WHERE datname = current_database();
            """)
            
            connection_stats = result.fetchone()
            
            return {
                "table_sizes": table_sizes,
                "active_connections": connection_stats[0],
                "active_queries": connection_stats[1],
                "status": "healthy"
            }
            
    except Exception as e:
                       logger.error(f"Database stats collection failed: {e}")
        return {"status": "error", "message": str(e)} 