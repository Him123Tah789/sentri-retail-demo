import json
import datetime
from typing import Dict, Any, Optional
from app.agent_gateway.intent_router import detect_intent
from app.agent_gateway.response_builder import build_reply
from app.llm.llm_router import llm_explain
from app.llm.prompts import SEC_EXPLAIN
# Security stub (keep your existing engines here)
from app.tools.security.stub import security_stub_scan

# File-based persistence to avoid losing history on reload
import os

# Store data outside app/backend to prevent reload loops
DATA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../data/conversations.json"))
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

def _load_conversations() -> Dict[str, list[dict]]:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading conversations: {e}")
        return {}

def _save_conversations(data: Dict[str, list[dict]]):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving conversations: {e}")

# Load initially
_CONV: Dict[str, list[dict]] = _load_conversations()

def _get_conv(cid: str) -> list[dict]:
    # Always reload to ensure multi-process sync (simple approach)
    global _CONV
    _CONV = _load_conversations()
    return _CONV.setdefault(cid, [])

def _save_conv(cid: str, messages: list[dict]):
    global _CONV
    _CONV[cid] = messages
    _save_conversations(_CONV)

def list_conversations() -> list[dict]:
    """List all conversations with preview."""
    # Reload to get latest
    global _CONV
    _CONV = _load_conversations()
    
    out = []
    for cid, msgs in _CONV.items():
        if not msgs:
            continue
        first = msgs[0]
        last = msgs[-1]
        out.append({
            "id": cid,
            "mode": first.get("mode", "security"),
            "preview": first.get("content", "")[:60],
            "timestamp": last.get("timestamp", datetime.datetime.now().isoformat()),
            "message_count": len(msgs)
        })
    # Sort by timestamp desc
    return sorted(out, key=lambda x: x["timestamp"], reverse=True)

def get_conversation(cid: str) -> list[dict]:
    """Get full conversation history."""
    # Reload for latest
    global _CONV
    _CONV = _load_conversations()
    return _CONV.get(cid, [])

def handle_chat(conversation_id: str, mode: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    intent = detect_intent(mode, message)
    tool_result = None
    ts = datetime.datetime.now().isoformat()

    # Load and append user message
    messages = _get_conv(conversation_id)
    messages.append({
        "role": "user", 
        "content": message, 
        "mode": mode,
        "timestamp": ts
    })
    _save_conv(conversation_id, messages)

    if mode == "security":
        if intent in ("scan_link", "scan_email", "scan_logs"):
            tool_result = security_stub_scan(intent=intent, text=message)

        system_extra = SEC_EXPLAIN
        llm_reply = llm_explain(
            user_message=message if tool_result is None else "Explain the scan result and next steps.",
            system_extra=system_extra,
            context_json=json.dumps(tool_result or {}, ensure_ascii=False)
        )
        
        # Reload to minimize race conditions, then append reply
        messages = _get_conv(conversation_id)
        messages.append({
            "role": "assistant", 
            "content": llm_reply, 
            "mode": mode,
            "timestamp": datetime.datetime.now().isoformat()
        })
        _save_conv(conversation_id, messages)
        
        return build_reply(intent, tool_result, llm_reply)

    # Automotive mode removed
    if mode == "automotive":
        llm_reply = "Sentri: Automotive mode is currently disabled."
        messages = _get_conv(conversation_id)
        messages.append({
            "role": "assistant", 
            "content": llm_reply, 
            "mode": mode,
            "timestamp": datetime.datetime.now().isoformat()
        })
        _save_conv(conversation_id, messages)
        return build_reply(intent, tool_result, llm_reply)

    # fallback
    llm_reply = "Sentri: Unsupported mode."
    messages = _get_conv(conversation_id)
    messages.append({
        "role": "assistant", 
        "content": llm_reply, 
        "mode": mode,
        "timestamp": datetime.datetime.now().isoformat()
    })
    _save_conv(conversation_id, messages)
    return build_reply(intent, tool_result, llm_reply)
