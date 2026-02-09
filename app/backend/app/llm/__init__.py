# LLM Layer - Pluggable Brain
# Gateway calls llm_router.generate(...) - switch models with zero rewrite

from .llm_router import LLMRouter
from .local_llm import LocalLLM
from .claude_llm import ClaudeLLM
from .gemini_llm import GeminiLLM

__all__ = [
    "LLMRouter",
    "LocalLLM",
    "ClaudeLLM",
    "GeminiLLM"
]
