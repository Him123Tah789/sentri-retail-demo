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
    resp = _client.responses.create(model=LLM_MODEL, input=messages, temperature=0.3)
    return resp.output_text
