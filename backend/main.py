#!/usr/bin/env python3
"""
SeatSync Backend - Main Entry Point
AI-Powered Sports Ticket Portfolio Management Platform
"""

import os
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable (Railway sets this)
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting SeatSync Backend on {host}:{port}")
    print(f"📊 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"🔗 API Documentation: http://{host}:{port}/docs")
    
    # Start the FastAPI server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    ) 