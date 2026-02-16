import uuid
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.agent_gateway.gateway import handle_chat, list_conversations, get_conversation

router = APIRouter()

@router.post("/assistant/chat", response_model=ChatResponse)
def assistant_chat(req: ChatRequest):
    cid = req.conversation_id or str(uuid.uuid4())
    result = handle_chat(
        conversation_id=cid,
        mode=req.mode,
        message=req.message,
        context=req.context
    )
    return ChatResponse(
        conversation_id=cid,
        mode=req.mode,
        intent=result["intent"],
        reply=result["reply"],
        tool_result=result.get("tool_result"),
    )

@router.get("/assistant/history")
def get_history():
    return {"conversations": list_conversations()}

@router.get("/assistant/history/{cid}")
def get_chat_history(cid: str):
    msgs = get_conversation(cid)
    if not msgs:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"messages": msgs}
