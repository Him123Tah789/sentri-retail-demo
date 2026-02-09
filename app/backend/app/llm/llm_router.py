"""
LLM Router - Pluggable Brain
=============================

Gateway calls: llm_router.generate(...)
Later you can switch models with zero rewrite.

Fallback Chain: Claude -> Gemini -> Local
"""

import os
import logging
from typing import Optional
from enum import Enum

from .local_llm import LocalLLM
from .claude_llm import ClaudeLLM
from .gemini_llm import GeminiLLM

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers"""
    CLAUDE = "claude"
    GEMINI = "gemini"
    LOCAL = "local"
    AUTO = "auto"  # Automatic fallback


class LLMRouter:
    """
    LLM Router - Pluggable AI Brain
    
    Switch between LLM providers without code changes.
    Automatic fallback chain: Claude -> Gemini -> Local
    
    Usage:
        router = LLMRouter()
        response = await router.generate("What is phishing?")
    """
    
    def __init__(self, preferred_provider: str = None):
        """
        Initialize LLM Router
        
        Args:
            preferred_provider: Preferred LLM ("claude", "gemini", "local", "auto")
        """
        # Get preferred provider from env or parameter
        provider_str = preferred_provider or os.getenv("LLM_PROVIDER", "auto")
        
        try:
            self.preferred = LLMProvider(provider_str.lower())
        except ValueError:
            self.preferred = LLMProvider.AUTO
        
        # Initialize all providers
        self.claude = ClaudeLLM()
        self.gemini = GeminiLLM()
        self.local = LocalLLM()
        
        # Track active provider
        self._last_provider = None
        
        logger.info(f"🧠 LLM Router initialized (preferred: {self.preferred.value})")
        self._log_availability()
    
    def _log_availability(self):
        """Log which providers are available"""
        providers = []
        if self.claude.is_available():
            providers.append("Claude ✅")
        if self.gemini.is_available():
            providers.append("Gemini ✅")
        providers.append("Local ✅")  # Always available
        
        logger.info(f"📊 Available LLMs: {', '.join(providers)}")
    
    def get_active_provider(self) -> str:
        """Get the currently active LLM provider"""
        if self._last_provider:
            return self._last_provider
        
        if self.preferred == LLMProvider.AUTO:
            if self.claude.is_available():
                return "claude"
            elif self.gemini.is_available():
                return "gemini"
            return "local"
        
        return self.preferred.value
    
    async def generate(
        self,
        prompt: str,
        context: str = None,
        max_tokens: int = 500
    ) -> str:
        """
        Generate response using the best available LLM
        
        Fallback Chain: Claude -> Gemini -> Local
        
        Args:
            prompt: User message/prompt
            context: Optional conversation context
            max_tokens: Maximum response tokens
            
        Returns:
            Generated response (never None - Local is always fallback)
        """
        # Try preferred provider first if not AUTO
        if self.preferred != LLMProvider.AUTO:
            response = await self._try_provider(
                self.preferred.value, prompt, context, max_tokens
            )
            if response:
                return response
        
        # Auto fallback chain
        # 1. Try Claude
        if self.claude.is_available():
            response = await self._try_provider("claude", prompt, context, max_tokens)
            if response:
                return response
        
        # 2. Try Gemini
        if self.gemini.is_available():
            response = await self._try_provider("gemini", prompt, context, max_tokens)
            if response:
                return response
        
        # 3. Fallback to Local (always works)
        self._last_provider = "local"
        logger.info("📚 Using Local knowledge base")
        return await self.local.generate(prompt, context)
    
    async def _try_provider(
        self,
        provider: str,
        prompt: str,
        context: str,
        max_tokens: int
    ) -> Optional[str]:
        """Try a specific provider"""
        try:
            if provider == "claude" and self.claude.is_available():
                response = await self.claude.generate(prompt, context, max_tokens)
                if response:
                    self._last_provider = "claude"
                    return response
            
            elif provider == "gemini" and self.gemini.is_available():
                response = await self.gemini.generate(prompt, context, max_tokens)
                if response:
                    self._last_provider = "gemini"
                    return response
            
            elif provider == "local":
                self._last_provider = "local"
                return await self.local.generate(prompt, context)
                
        except Exception as e:
            logger.warning(f"⚠️ {provider} failed: {str(e)[:50]}")
        
        return None
    
    async def chat(self, message: str, context: str = None) -> str:
        """Chat using best available LLM"""
        return await self.generate(message, context)
    
    async def answer_security_question(
        self,
        question: str,
        context: str = None
    ) -> str:
        """Answer security question"""
        # Try specialized methods first
        if self.preferred != LLMProvider.AUTO:
            provider = self._get_provider(self.preferred.value)
            if provider and provider.is_available():
                response = await provider.answer_security_question(question, context)
                if response:
                    self._last_provider = self.preferred.value
                    return response
        
        # Fallback chain
        if self.claude.is_available():
            response = await self.claude.answer_security_question(question, context)
            if response:
                self._last_provider = "claude"
                return response
        
        if self.gemini.is_available():
            response = await self.gemini.answer_security_question(question, context)
            if response:
                self._last_provider = "gemini"
                return response
        
        self._last_provider = "local"
        return await self.local.answer_security_question(question, context)
    
    async def explain_scan(
        self,
        scan_type: str,
        scan_result: dict,
        context: str = None
    ) -> Optional[str]:
        """
        Explain scan result using LLM
        
        Returns None if only local is available (let tool result speak)
        """
        # Try Claude first
        if self.claude.is_available():
            response = await self.claude.explain_scan(scan_type, scan_result, context)
            if response:
                self._last_provider = "claude"
                return response
        
        # Try Gemini
        if self.gemini.is_available():
            response = await self.gemini.explain_scan(scan_type, scan_result, context)
            if response:
                self._last_provider = "gemini"
                return response
        
        # Local doesn't add extra explanation
        return None
    
    def _get_provider(self, name: str):
        """Get provider by name"""
        providers = {
            "claude": self.claude,
            "gemini": self.gemini,
            "local": self.local
        }
        return providers.get(name)
    
    def get_status(self) -> dict:
        """Get LLM router status"""
        return {
            "preferred": self.preferred.value,
            "active": self.get_active_provider(),
            "last_used": self._last_provider,
            "providers": {
                "claude": {
                    "available": self.claude.is_available(),
                    "model": self.claude.model if self.claude.is_available() else None
                },
                "gemini": {
                    "available": self.gemini.is_available(),
                    "model": self.gemini.model_name if self.gemini.is_available() else None
                },
                "local": {
                    "available": True,
                    "type": "knowledge_base"
                }
            }
        }
