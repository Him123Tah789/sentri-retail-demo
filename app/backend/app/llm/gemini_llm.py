"""
Gemini LLM - Google Integration
===============================

Integration with Google's Gemini API.
Requires GEMINI_API_KEY environment variable.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import google generativeai
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("⚠️ google-generativeai package not installed")


class GeminiLLM:
    """
    Gemini LLM - Google AI Integration
    
    Provides AI capabilities via Google's Gemini.
    Falls back gracefully if API key not set.
    """
    
    SYSTEM_PROMPT = """You are Sentri, an AI security assistant for retail businesses.

Your expertise:
- Cybersecurity threat analysis
- Phishing detection and prevention
- Security best practices
- Risk assessment

Guidelines:
- Be concise but thorough
- Use bullet points for clarity
- Provide actionable advice
- Explain technical terms simply
- Focus on practical security tips

You can analyze:
- Suspicious URLs and links
- Phishing emails
- Security logs
- General security questions"""

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize Gemini LLM
        
        Args:
            api_key: Google API key (or from env)
            model: Gemini model to use
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.model = None
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"✅ Gemini LLM initialized (model: {self.model_name})")
            except Exception as e:
                logger.error(f"❌ Gemini initialization error: {e}")
        else:
            logger.info("⚠️ Gemini LLM not configured")
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self.model is not None
    
    async def generate(
        self,
        prompt: str,
        context: str = None,
        max_tokens: int = 500
    ) -> Optional[str]:
        """
        Generate response using Gemini
        
        Args:
            prompt: User message
            context: Optional conversation context
            max_tokens: Maximum response tokens
            
        Returns:
            Generated response or None if unavailable
        """
        if not self.model:
            return None
        
        try:
            full_prompt = f"{self.SYSTEM_PROMPT}\n\n"
            if context:
                full_prompt += f"Previous context:\n{context}\n\n"
            full_prompt += f"User message:\n{prompt}"
            
            response = self.model.generate_content(full_prompt)
            
            logger.info("✅ Gemini response generated")
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Gemini error: {str(e)[:100]}")
            return None
    
    async def chat(self, message: str, context: str = None) -> Optional[str]:
        """Chat using Gemini"""
        return await self.generate(message, context)
    
    async def answer_security_question(
        self,
        question: str,
        context: str = None
    ) -> Optional[str]:
        """Answer security question"""
        enhanced_prompt = f"""Security question:
{question}

Provide a helpful, concise answer with:
- Clear explanation
- Practical advice
- Actionable steps"""
        
        return await self.generate(enhanced_prompt, context)
    
    async def explain_scan(
        self,
        scan_type: str,
        scan_result: dict,
        context: str = None
    ) -> Optional[str]:
        """
        Generate explanation for scan result
        
        Args:
            scan_type: Type of scan (link, email, logs)
            scan_result: Result from scanning tool
            context: Optional conversation context
            
        Returns:
            Human-friendly explanation
        """
        if not self.model:
            return None
        
        risk_level = scan_result.get("risk_level", "UNKNOWN")
        risk_score = scan_result.get("risk_score", 0)
        signals = scan_result.get("signals", [])
        
        prompt = f"""Explain this {scan_type} scan result briefly (2-3 sentences):

Risk: {risk_level} ({risk_score}/100)
Signals: {', '.join(signals[:5])}

Why this risk level? What should user do?"""
        
        return await self.generate(prompt, context, max_tokens=200)
