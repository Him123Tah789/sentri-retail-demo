"""
Claude LLM - Anthropic Integration
==================================

Integration with Anthropic's Claude API.
Requires ANTHROPIC_API_KEY environment variable.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import anthropic
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("⚠️ anthropic package not installed")


class ClaudeLLM:
    """
    Claude LLM - Anthropic API Integration
    
    Provides advanced AI capabilities via Claude.
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
        Initialize Claude LLM
        
        Args:
            api_key: Anthropic API key (or from env)
            model: Claude model to use
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
        self.client = None
        
        if ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info(f"✅ Claude LLM initialized (model: {self.model})")
            except Exception as e:
                logger.error(f"❌ Claude initialization error: {e}")
        else:
            logger.info("⚠️ Claude LLM not configured (no API key)")
    
    def is_available(self) -> bool:
        """Check if Claude is available"""
        return self.client is not None
    
    async def generate(
        self,
        prompt: str,
        context: str = None,
        max_tokens: int = 500
    ) -> Optional[str]:
        """
        Generate response using Claude
        
        Args:
            prompt: User message
            context: Optional conversation context
            max_tokens: Maximum response tokens
            
        Returns:
            Generated response or None if unavailable
        """
        if not self.client:
            return None
        
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Previous context:\n{context}\n\nUser message:\n{prompt}"
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            logger.info("✅ Claude response generated")
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"❌ Claude error: {str(e)[:100]}")
            return None
    
    async def chat(self, message: str, context: str = None) -> Optional[str]:
        """Chat using Claude"""
        return await self.generate(message, context)
    
    async def answer_security_question(
        self,
        question: str,
        context: str = None
    ) -> Optional[str]:
        """Answer security question"""
        enhanced_prompt = f"""Security question from user:
{question}

Provide a helpful, concise answer focusing on:
- Clear explanation of concepts
- Practical security advice
- Actionable steps when relevant"""
        
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
        if not self.client:
            return None
        
        risk_level = scan_result.get("risk_level", "UNKNOWN")
        risk_score = scan_result.get("risk_score", 0)
        signals = scan_result.get("signals", [])
        
        prompt = f"""Explain this {scan_type} scan result in 2-3 sentences:

Risk Level: {risk_level}
Risk Score: {risk_score}/100
Signals: {', '.join(signals[:5])}

Focus on:
- Why this risk level was assigned
- What the user should do
- Keep it brief and clear"""
        
        return await self.generate(prompt, context, max_tokens=200)
