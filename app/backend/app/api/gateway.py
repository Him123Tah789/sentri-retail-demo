"""
Gateway API - Universal endpoint for all channels
Routes through the Sentri Agent Gateway PRO
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from ..db.database import get_database
from ..db.models import User
from ..core.security import get_current_user

# PRO Architecture imports
from ..agent_gateway import SentriGateway, Intent
from ..tools import ToolsManager
from ..llm import LLMRouter

router = APIRouter()

# Initialize the PRO Gateway with all layers
_tools_manager = ToolsManager()
_llm_router = LLMRouter()
_gateway = SentriGateway(tools=_tools_manager, llm_router=_llm_router)


class GatewayRequest(BaseModel):
    """Universal gateway request"""
    message: str
    channel: str = "api"  # api, telegram, web
    metadata: Optional[Dict[str, Any]] = None


class GatewayResponseModel(BaseModel):
    """Gateway response with full context"""
    text: str
    intent: str
    confidence: float = 0.0
    suggested_actions: List[str] = []
    tool_used: Optional[str] = None
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    scan_result: Optional[Dict[str, Any]] = None
    success: bool = True


@router.post("/message", response_model=GatewayResponseModel)
async def gateway_message(
    request: GatewayRequest,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Universal gateway endpoint - routes messages to appropriate tools.
    
    PRO Architecture: All platforms → ONE gateway → Sentri Brain
    
    The gateway automatically detects intent:
    - URLs → Risk Engine (phishing detection)
    - "scan email" → Email analysis
    - "scan log" → Log analysis  
    - General text → LLM chat with fallback chain
    """
    try:
        # Use the PRO Gateway
        response = await _gateway.process_message(
            user_id=str(current_user.id),
            message=request.message,
            platform=request.channel,
            metadata=request.metadata
        )
        
        # Extract metadata for response
        meta = response.metadata or {}
        
        return GatewayResponseModel(
            text=response.text,
            intent=response.intent.value if response.intent else "unknown",
            confidence=response.confidence,
            suggested_actions=response.suggested_actions,
            tool_used=meta.get("tool_used"),
            risk_score=meta.get("risk_score"),
            risk_level=meta.get("risk_level"),
            scan_result=meta.get("scan_result"),
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def gateway_health():
    """Gateway health check - PRO Architecture"""
    return {
        "status": "healthy",
        "gateway": "Sentri PRO",
        "architecture": "layered",
        "layers": {
            "channels": "active",
            "agent_gateway": "active", 
            "tools": "active",
            "llm": "active",
            "memory": "active",
            "rag": "placeholder"
        }
    }


@router.get("/capabilities")
async def gateway_capabilities():
    """List PRO gateway capabilities"""
    return {
        "intents": [intent.value for intent in Intent],
        "channels": ["api", "telegram", "web", "mobile"],
        "layers": {
            "channels": {
                "description": "Platform adapters - same intelligence everywhere",
                "adapters": ["TelegramAdapter", "WebAdapter", "MobileAdapter"]
            },
            "agent_gateway": {
                "description": "The Brain - intent routing, memory, response building",
                "components": ["IntentRouter", "MemoryManager", "ResponseBuilder"]
            },
            "tools": {
                "description": "Risk engines for security analysis",
                "engines": ["LinkScanner", "EmailScanner", "LogsScanner", "GuardianStatus"]
            },
            "llm": {
                "description": "Pluggable AI with fallback chain",
                "providers": ["Claude", "Gemini", "Local"],
                "fallback_order": ["claude", "gemini", "local"]
            },
            "memory": {
                "description": "Cross-platform conversation storage",
                "features": ["Conversation history", "Summary engine", "Context tags"]
            },
            "rag": {
                "description": "Knowledge base retrieval (placeholder)",
                "status": "coming_soon"
            }
        },
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


@router.get("/stats")
async def gateway_stats():
    """Get gateway statistics"""
    return _gateway.get_stats()
