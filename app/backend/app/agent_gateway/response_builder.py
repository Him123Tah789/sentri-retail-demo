from typing import Optional, Dict, Any

def build_reply(intent: str, tool_result: Optional[Dict[str, Any]], llm_reply: str) -> Dict[str, Any]:
    return {
        "intent": intent,
        "reply": llm_reply,
        "tool_result": tool_result
    }
