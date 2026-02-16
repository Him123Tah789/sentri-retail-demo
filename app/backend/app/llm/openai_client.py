from openai import OpenAI
from app.core.config import OPENAI_API_KEY, LLM_MODEL
from app.llm.prompts import SYSTEM_SENTRI

_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def generate_text(user_message: str, system_extra: str = "", context_json: str = "") -> str:
    if not _client:
        return "Sentri: (OpenAI client not configured) Showing computed results."
    
    messages = [
        {"role": "system", "content": SYSTEM_SENTRI + "\n" + system_extra},
        {"role": "user", "content": f"{user_message}\n\nCONTEXT JSON:\n{context_json}".strip()}
    ]
    
    # Optimized call with timeout and token limit
    resp = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=400,  # Cap length for speed
        timeout=10.0     # Fail fast (10s)
    )
    return resp.choices[0].message.content or ""
