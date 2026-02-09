"""
AI Assistant chat endpoint - integrates rules engine with LLM explanations
"""
from typing import Optional, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..db.database import get_database
from ..db.models import User, Conversation, Message, ConversationMemory
from ..core.security import get_current_user
from ..services.assistant_engine import generate_response_async
from ..services.llm_service import llm_service

router = APIRouter()


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str
    context: Optional[Dict] = None


class ScanResult(BaseModel):
    """Structured scan result from the rules engine"""
    kind: str  # 'link', 'email', 'logs'
    input_preview: str
    risk_score: int
    risk_level: str
    verdict: str
    explanation: str
    recommended_actions: list


class RiskSummary(BaseModel):
    """Brief risk summary for quick display"""
    level: str  # HIGH, MEDIUM, LOW
    score: int  # 0-100
    verdict: str  # Short verdict
    action_required: bool  # Whether user needs to take action


class ChatResponse(BaseModel):
    conversation_id: int
    reply: str
    tool_used: str = "none"  # scan_link, scan_email, scan_logs, or none
    risk_summary: Optional[RiskSummary] = None  # Quick risk info
    scan_result: Optional[ScanResult] = None  # Full scan data
    scan_type: Optional[str] = None  # Legacy: link, email, logs


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Send a message to the AI assistant with conversation memory"""
    
    # Get or create conversation
    if request.conversation_id:
        conversation = db.query(Conversation)\
            .filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            ).first()
        
        if not conversation:
            # Create new if not found
            conversation = Conversation(user_id=current_user.id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
    else:
        # Create new conversation
        conversation = Conversation(user_id=current_user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Load conversation memory (summary + topics)
    memory = db.query(ConversationMemory)\
        .filter(ConversationMemory.conversation_id == conversation.id)\
        .first()
    
    memory_summary = memory.summary if memory else ""
    topics_covered = memory.topics_covered if memory else ""
    
    # Fetch conversation history (last 10 messages for context)
    history = db.query(Message)\
        .filter(Message.conversation_id == conversation.id)\
        .order_by(Message.id.desc())\
        .limit(10)\
        .all()
    
    # Reverse to chronological order and format for LLM
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(history)
    ]
    
    # Store user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    
    # Generate AI response with conversation history AND memory
    assistant_response = await generate_response_async(
        message=request.message,
        context=request.context,
        conversation_history=conversation_history,
        memory_summary=memory_summary,
        topics_covered=topics_covered
    )
    
    # Store assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=assistant_response.reply
    )
    db.add(assistant_message)
    
    # Update conversation memory after every exchange
    new_messages = conversation_history + [
        {"role": "user", "content": request.message},
        {"role": "assistant", "content": assistant_response.reply}
    ]
    
    # Generate updated summary (async but we await it)
    try:
        updated_summary = await llm_service.generate_summary(
            previous_summary=memory_summary,
            new_messages=new_messages[-4:]  # Last 4 messages
        )
        updated_topics = llm_service.extract_topics(
            updated_summary, 
            request.message
        )
    except Exception:
        # If summary generation fails, keep existing
        updated_summary = memory_summary
        updated_topics = topics_covered
    
    # Save or update conversation memory
    if memory:
        memory.summary = updated_summary
        memory.topics_covered = updated_topics
    else:
        memory = ConversationMemory(
            conversation_id=conversation.id,
            summary=updated_summary,
            topics_covered=updated_topics
        )
        db.add(memory)
    
    db.commit()
    
    # Build response with tool info and optional scan result
    response = ChatResponse(
        conversation_id=conversation.id,
        reply=assistant_response.reply,
        tool_used=assistant_response.tool_used,
        scan_type=assistant_response.scan_type
    )
    
    # Add risk summary if present
    if assistant_response.risk_summary:
        response.risk_summary = RiskSummary(**assistant_response.risk_summary)
    
    # Add scan result if present
    if assistant_response.scan_result:
        response.scan_result = ScanResult(**assistant_response.scan_result)
    
    return response


@router.get("/conversation/{conversation_id}")
async def get_conversation_history(
    conversation_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get conversation history by ID"""
    
    # Verify conversation belongs to user
    conversation = db.query(Conversation)\
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
    
    if not conversation:
        return {"conversation_id": conversation_id, "messages": []}
    
    # Fetch all messages for this conversation
    messages = db.query(Message)\
        .filter(Message.conversation_id == conversation_id)\
        .order_by(Message.id.asc())\
        .all()
    
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            }
            for msg in messages
        ]
    }
