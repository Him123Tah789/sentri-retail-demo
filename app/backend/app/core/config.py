import os
from dotenv import load_dotenv

load_dotenv()

SENTRI_MODE = os.getenv("SENTRI_MODE", "HACKATHON")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")