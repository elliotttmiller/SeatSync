import logging
from fastapi import FastAPI, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import traceback
import json
import os

from app.core.config import settings
from app.api.v1.api import api_router
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

# Set up logging
logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
logger = logging.getLogger("seatsync")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.debug(f"Request: {request.method} {request.url}")
        try:
            body = await request.body()
            logger.debug(f"Request body: {body.decode('utf-8')[:1000]}")
        except Exception:
            logger.debug("Could not read request body.")
        response = await call_next(request)
        logger.debug(f"Response status: {response.status_code}")
        if hasattr(response, 'body_iterator'):
            # Don't consume streaming responses
            logger.debug("Streaming response.")
        else:
            try:
                resp_body = b""
                async for chunk in response.body_iterator:
                    resp_body += chunk
                logger.debug(f"Response body: {resp_body.decode('utf-8')[:1000]}")
                response.body_iterator = iter([resp_body])
            except Exception:
                logger.debug("Could not read response body.")
        return response

app = FastAPI(
    title="SeatSync API",
    description="AI-Powered Sports Ticket Portfolio Management Platform",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(LoggingMiddleware)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "trace": traceback.format_exc().splitlines()[-3:]},
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to SeatSync API"}

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Railway specific: Use PORT environment variable
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    ) 