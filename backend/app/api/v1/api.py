from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, tickets, listings, analytics, marketplace
from app.api.v1.endpoints import refresh, predict, chat, automation

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(listings.router, prefix="/listings", tags=["listings"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(marketplace.router, prefix="/marketplace", tags=["marketplace"])
api_router.include_router(refresh.router, prefix="/auth", tags=["auth"])
api_router.include_router(predict.router, tags=["ai"])
api_router.include_router(chat.router, tags=["ai"])
api_router.include_router(automation.router, prefix="/automation", tags=["automation", "ai"]) 