"""
Gateway API - Universal endpoint for all channels
Routes through the Sentri Agent Gateway
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any

from ..db.database import get_database
from ..db.models import User
from ..core.security import get_current_user
from ..services.agent_gateway import process_message, AgentResponse, IntentType

router = APIRouter()


class GatewayRequest(BaseModel):
    """Universal gateway request"""
    message: str
    channel: str = "api"  # api, telegram, web
    metadata: Optional[Dict[str, Any]] = None


class GatewayResponse(BaseModel):
    """Gateway response with full context"""
    text: str
    intent: str
    tool_used: Optional[str] = None
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    scan_result: Optional[Dict[str, Any]] = None
    success: bool = True


@router.post("/message", response_model=GatewayResponse)
async def gateway_message(
    request: GatewayRequest,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Universal gateway endpoint - routes messages to appropriate tools.
    
    The gateway automatically detects intent:
    - URLs → Risk Engine (phishing detection)
    - "scan email" → Email analysis
    - "scan log" → Log analysis
    - General text → LLM chat
    """
    try:
        response: AgentResponse = await process_message(
            text=request.message,
            user_id=str(current_user.id),
            channel=request.channel
        )
        
        return GatewayResponse(
            text=response.text,
            intent=response.intent.value,
            tool_used=response.tool_used,
            risk_score=response.risk_score,
            risk_level=response.risk_level,
            scan_result=response.scan_result,
            success=response.success
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def gateway_health():
    """Gateway health check"""
    return {
        "status": "healthy",
        "gateway": "online",
        "tools": {
            "risk_engine": "active",
            "llm_service": "ready",
            "telegram_bot": "configurable"
        }
    }


@router.get("/capabilities")
async def gateway_capabilities():
    """List gateway capabilities"""
    return {
        "intents": [intent.value for intent in IntentType],
        "channels": ["api", "telegram", "web"],
        "tools": [
            {
                "name": "risk_engine",
                "description": "Phishing/fraud detection for links, emails, logs",
                "types": ["link", "email", "log"]
            },
            {
                "name": "llm_service",
                "description": "AI chat and explanations",
                "types": ["general_chat", "summary"]
            },
            {
                "name": "local_knowledge",
                "description": "Built-in knowledge base for common questions",
                "types": ["tech", "security", "general"]
            }
        ]
    }
