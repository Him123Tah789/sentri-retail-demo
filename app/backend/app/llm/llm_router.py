from app.core.config import LLM_PROVIDER, OPENAI_API_KEY
from app.llm.openai_client import generate_text

def llm_explain(user_message: str, system_extra: str, context_json: str) -> str:
    """Route to LLM provider with hackathon-safe fallback."""
    if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        try:
            return generate_text(user_message, system_extra=system_extra, context_json=context_json)
        except Exception:
            return "Sentri: (LLM temporarily unavailable) I can show the computed results and recommended next steps."
    return "Sentri: (LLM disabled) I can show the computed results and recommended next steps."
