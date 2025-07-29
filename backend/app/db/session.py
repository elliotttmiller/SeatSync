import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.core.config import settings

# --- Setup logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Create async engine ---
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# --- Create async session factory ---
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# --- Async DB health check ---
async def check_db_health() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

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