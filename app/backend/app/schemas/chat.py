from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal

Mode = Literal["security", "automotive"]

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None   # hackathon simple string id
    mode: Mode
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    conversation_id: str
    mode: Mode
    intent: str
    reply: str
    tool_result: Optional[Dict[str, Any]] = None
