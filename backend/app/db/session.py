import time
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError
from app.core.config import settings

# --- Setup logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database_engine_with_retry():
    """
    Creates a robust SQLAlchemy engine with a retry loop to handle startup race conditions in cloud environments.
    """
    database_url = settings.DATABASE_URL
    if not database_url:
        logger.critical("FATAL: DATABASE_URL is not set in the environment.")
        raise ValueError("DATABASE_URL is not set.")

    engine_config = {
        "poolclass": QueuePool,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "echo": settings.DEBUG,
    }

    max_retries = 10
    retry_delay_seconds = 5
    logger.info("Attempting to create database engine...")

    for attempt in range(max_retries):
        try:
            engine = create_engine(database_url, **engine_config)
            # Test the connection to ensure the database is ready
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"---> Database connection successful on attempt {attempt + 1} <---")
            return engine
        except OperationalError as e:
            logger.warning(f"Connection attempt {attempt + 1} of {max_retries} failed. Database may not be ready yet.")
            if attempt + 1 < max_retries:
                logger.info(f"Retrying in {retry_delay_seconds} seconds...")
                time.sleep(retry_delay_seconds)
            else:
                logger.critical("Could not connect to the database after all retries.")
                raise  # Re-raise the last exception to crash the app if it truly can't connect
    raise Exception("Failed to create a database engine after multiple retries.")

# --- Create the engine instance using our new robust function ---
engine = create_database_engine_with_retry()

# --- The rest of your professional setup remains the same ---

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
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'timescaledb'"))
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
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

def get_db_stats():
    """Get database statistics"""
    try:
        with engine.connect() as conn:
            # Get table sizes
            result = conn.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
            """))
            table_sizes = result.fetchall()
            # Get connection info
            result = conn.execute(text("""
                SELECT 
                    count(*) as active_connections,
                    count(*) FILTER (WHERE state = 'active') as active_queries
                FROM pg_stat_activity 
                WHERE datname = current_database();
            """))
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