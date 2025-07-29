from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, tickets, listings, analytics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(listings.router, prefix="/listings", tags=["listings"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"]) 