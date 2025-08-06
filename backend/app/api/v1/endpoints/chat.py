from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.ai_service import AIService
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize AI service
ai_service = AIService()

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []
    user_context: Optional[Dict[str, Any]] = {}
    portfolio_context: Optional[bool] = True

class PortfolioInsightsRequest(BaseModel):
    user_id: Optional[str] = None
    include_recommendations: bool = True
    include_alerts: bool = True

@router.post("/chat")
async def chat_with_ai(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Intelligent conversational AI for ticket portfolio management
    
    Provides AI-powered assistance with ticket pricing, portfolio optimization,
    market analysis, and strategic recommendations based on user data and context.
    """
    try:
        logger.info(f"Processing chat message: {request.message[:50]}...")
        
        # Build conversation context
        conversation_context = ""
        if request.conversation_history:
            context_messages = []
            for msg in request.conversation_history[-5:]:  # Last 5 messages for context
                context_messages.append(f"{msg.role}: {msg.content}")
            conversation_context = "\n".join(context_messages)
        
        # Get user portfolio context if requested
        portfolio_context = ""
        if request.portfolio_context and request.user_context.get("user_id"):
            try:
                portfolio_insights = await ai_service.generate_portfolio_insights(
                    user_id=request.user_context["user_id"],
                    db=db
                )
                portfolio_context = f"User Portfolio Summary: {portfolio_insights.get('summary', {})}"
            except Exception as e:
                logger.warning(f"Could not fetch portfolio context: {e}")
        
        # Build comprehensive AI prompt for chat
        chat_prompt = _build_chat_prompt(
            user_message=request.message,
            conversation_context=conversation_context,
            portfolio_context=portfolio_context,
            user_context=request.user_context
        )
        
        # Generate AI response
        ai_response = await ai_service._generate_ai_response(chat_prompt)
        
        # Clean up the response
        cleaned_response = _clean_chat_response(ai_response)
        
        return {
            "status": "success",
            "response": cleaned_response,
            "conversation_id": request.user_context.get("conversation_id", "default"),
            "suggestions": _generate_response_suggestions(request.message, cleaned_response)
        }
        
    except Exception as e:
        logger.error(f"Chat AI error: {e}")
        return {
            "status": "error",
            "response": "I apologize, but I'm experiencing technical difficulties. Please try again later or contact support if the issue persists.",
            "error": str(e)
        }

@router.post("/portfolio-insights")
async def get_portfolio_insights(
    request: PortfolioInsightsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate comprehensive AI-driven portfolio insights and recommendations
    
    Analyzes user's ticket portfolio to provide strategic insights,
    optimization recommendations, and proactive alerts.
    """
    try:
        # Default to first user if no user_id provided (for demo)
        user_id = request.user_id
        if not user_id:
            from app.models.database import User
            from sqlalchemy import select
            user_result = await db.execute(select(User).limit(1))
            user = user_result.scalar_one_or_none()
            if user:
                user_id = str(user.id)
            else:
                raise HTTPException(status_code=404, detail="No user found")
        
        logger.info(f"Generating portfolio insights for user: {user_id}")
        
        # Generate comprehensive insights
        insights = await ai_service.generate_portfolio_insights(
            user_id=user_id,
            db=db
        )
        
        response = {
            "status": "success",
            "user_id": user_id,
            "insights": insights
        }
        
        # Filter response based on request parameters
        if not request.include_recommendations:
            response["insights"].pop("recommendations", None)
        if not request.include_alerts:
            response["insights"].pop("alerts", None)
            
        return response
        
    except Exception as e:
        logger.error(f"Portfolio insights error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Portfolio insights generation failed: {str(e)}"
        )

def _build_chat_prompt(
    user_message: str,
    conversation_context: str,
    portfolio_context: str,
    user_context: Dict[str, Any]
) -> str:
    """Build comprehensive chat prompt for AI assistant"""
    
    base_persona = """
You are SeatSync AI, an expert ticket portfolio management assistant. You help users:
- Optimize their sports ticket investments
- Analyze market trends and pricing strategies  
- Make informed buying and selling decisions
- Understand portfolio performance and ROI
- Navigate marketplace integrations

You provide clear, actionable advice with specific recommendations when possible.
"""
    
    context_sections = []
    
    if conversation_context:
        context_sections.append(f"Recent Conversation:\n{conversation_context}")
    
    if portfolio_context:
        context_sections.append(f"Portfolio Context:\n{portfolio_context}")
    
    if user_context:
        context_sections.append(f"User Context:\n{user_context}")
    
    full_context = "\n\n".join(context_sections) if context_sections else "No additional context available."
    
    return f"""{base_persona}

CONTEXT:
{full_context}

USER MESSAGE: {user_message}

Provide a helpful, personalized response based on the context above. Be conversational but professional. If you need more information to provide specific advice, ask clarifying questions."""

def _clean_chat_response(response: str) -> str:
    """Clean and format AI chat response"""
    # Remove any JSON formatting if present
    if response.strip().startswith('{') and response.strip().endswith('}'):
        try:
            import json
            parsed = json.loads(response)
            response = parsed.get('response', response)
        except:
            pass
    
    # Basic cleanup
    response = response.strip()
    
    # Remove any system artifacts
    response = response.replace("```json", "").replace("```", "")
    
    return response

def _generate_response_suggestions(user_message: str, ai_response: str) -> List[str]:
    """Generate follow-up suggestions based on the conversation"""
    
    # Basic keyword-based suggestions
    suggestions = []
    
    user_lower = user_message.lower()
    
    if "price" in user_lower or "pricing" in user_lower:
        suggestions.extend([
            "How do I optimize my listing prices?",
            "Show me market trends for this team",
            "When is the best time to sell?"
        ])
    
    if "portfolio" in user_lower or "performance" in user_lower:
        suggestions.extend([
            "Analyze my portfolio performance",
            "What are my best and worst investments?",
            "How can I diversify my holdings?"
        ])
    
    if "market" in user_lower or "trend" in user_lower:
        suggestions.extend([
            "What teams are trending up?",
            "Show me seasonal patterns",
            "Predict market movements"
        ])
    
    # Default suggestions if none match
    if not suggestions:
        suggestions = [
            "Analyze my current portfolio",
            "Get price predictions for my tickets",
            "Show me market opportunities"
        ]
    
    return suggestions[:3]  # Return max 3 suggestions 