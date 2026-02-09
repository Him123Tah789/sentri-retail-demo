"""
Sentri Gateway - THE BRAIN ROUTER
=================================

This is the MOST important layer.

All platforms talk to ONE gateway.
That means:
✅ Same intelligence everywhere
✅ No duplicated logic
✅ Add new platforms in minutes

Gateway Flow:
    Incoming Message
           ↓
    Intent Router
           ↓
    Memory Manager
           ↓
    Tool Execution (if needed)
           ↓
    LLM Response Builder
           ↓
    Return to channel
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

from .intent_router import IntentRouter, Intent, IntentResult
from .memory_manager import MemoryManager
from .response_builder import ResponseBuilder, FormattedResponse

logger = logging.getLogger(__name__)


@dataclass
class GatewayResponse:
    """Response from the Gateway"""
    text: str
    intent: Intent
    confidence: float
    suggested_actions: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "intent": self.intent.value if self.intent else None,
            "confidence": self.confidence,
            "suggested_actions": self.suggested_actions,
            "metadata": self.metadata
        }


class SentriGateway:
    """
    Sentri Agent Gateway - The Brain
    
    This is the central nervous system of Sentri.
    All platforms route through here.
    
    Responsibilities:
    ✔ Detect intent
    ✔ Load memory
    ✔ Call tools (risk engines)
    ✔ Call LLM
    ✔ Save memory
    ✔ Format response
    """
    
    def __init__(
        self,
        tools=None,
        llm_router=None,
        memory_manager: MemoryManager = None,
        intent_router: IntentRouter = None,
        response_builder: ResponseBuilder = None
    ):
        """
        Initialize Sentri Gateway
        
        Args:
            tools: Tool layer for risk scanning
            llm_router: LLM layer for AI responses
            memory_manager: Memory layer for conversation history
            intent_router: Intent detection
            response_builder: Response formatting
        """
        # Core components
        self.tools = tools
        self.llm_router = llm_router
        
        # Initialize layers
        self.memory = memory_manager or MemoryManager()
        self.intent_router = intent_router or IntentRouter()
        self.response_builder = response_builder or ResponseBuilder()
        
        # Statistics
        self._stats = {
            "total_messages": 0,
            "scans_performed": 0,
            "intents": {}
        }
        
        logger.info("🚀 Sentri Gateway initialized")
    
    def set_tools(self, tools):
        """Set the tools layer"""
        self.tools = tools
        logger.info("🔧 Tools layer connected")
    
    def set_llm(self, llm_router):
        """Set the LLM router"""
        self.llm_router = llm_router
        logger.info("🧠 LLM layer connected")
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        platform: str = "web",
        metadata: dict = None
    ) -> GatewayResponse:
        """
        Process incoming message - THE MAIN ENTRY POINT
        
        This is where all the magic happens.
        
        Args:
            user_id: User identifier
            message: User's message
            platform: Source platform (telegram, web, mobile)
            metadata: Additional context
            
        Returns:
            GatewayResponse with processed result
        """
        self._stats["total_messages"] += 1
        
        try:
            # Step 1: Detect Intent
            intent_result = self.intent_router.detect_intent(message)
            intent = intent_result.intent
            
            logger.info(f"📨 [{platform}] Intent: {intent.value} ({intent_result.confidence:.0%})")
            
            # Track intent stats
            self._stats["intents"][intent.value] = self._stats["intents"].get(intent.value, 0) + 1
            
            # Step 2: Load Memory
            context = self.memory.get_context_string(user_id, platform)
            
            # Step 3: Route to appropriate handler
            response = await self._route_intent(
                intent_result=intent_result,
                message=message,
                user_id=user_id,
                platform=platform,
                context=context,
                metadata=metadata
            )
            
            # Step 4: Save to Memory
            self.memory.save_memory(
                user_id=user_id,
                user_message=message,
                assistant_reply=response.text,
                platform=platform,
                intent=intent.value,
                metadata=metadata
            )
            
            # Step 5: Format for platform
            formatted = self.response_builder.format_for_platform(
                FormattedResponse(
                    text=response.text,
                    intent=response.intent,
                    confidence=response.confidence,
                    suggested_actions=response.suggested_actions,
                    metadata=response.metadata
                ),
                platform
            )
            
            return GatewayResponse(
                text=formatted.text,
                intent=formatted.intent,
                confidence=formatted.confidence,
                suggested_actions=formatted.suggested_actions,
                metadata=formatted.metadata
            )
            
        except Exception as e:
            logger.error(f"Gateway error: {e}")
            error_response = self.response_builder.build_error_response("general", str(e))
            return GatewayResponse(
                text=error_response.text,
                intent=Intent.UNKNOWN,
                confidence=0.0,
                suggested_actions=error_response.suggested_actions
            )
    
    async def _route_intent(
        self,
        intent_result: IntentResult,
        message: str,
        user_id: str,
        platform: str,
        context: str,
        metadata: dict
    ) -> FormattedResponse:
        """
        Route to appropriate handler based on intent
        
        Args:
            intent_result: Detected intent
            message: Original message
            user_id: User ID
            platform: Platform
            context: Conversation context
            metadata: Additional metadata
            
        Returns:
            FormattedResponse
        """
        intent = intent_result.intent
        
        # ==========================================
        # SCAN INTENTS - Use Tools
        # ==========================================
        
        if intent == Intent.SCAN_LINK:
            return await self._handle_scan_link(
                intent_result.extracted_data.get("urls", []),
                message, context
            )
        
        if intent == Intent.SCAN_EMAIL:
            return await self._handle_scan_email(message, context)
        
        if intent == Intent.SCAN_LOGS:
            return await self._handle_scan_logs(message, context)
        
        # ==========================================
        # STATUS/HELP INTENTS
        # ==========================================
        
        if intent == Intent.GUARDIAN_STATUS:
            return await self._handle_status()
        
        if intent == Intent.HELP:
            return self.response_builder.build_help_response(platform)
        
        if intent == Intent.GREETING:
            username = metadata.get("username") if metadata else None
            return self.response_builder.build_greeting_response(username, platform)
        
        # ==========================================
        # CHAT INTENTS - Use LLM
        # ==========================================
        
        if intent == Intent.SECURITY_QUESTION:
            return await self._handle_security_question(message, context)
        
        # Default: General chat
        return await self._handle_general_chat(message, context)
    
    # ==========================================
    # Intent Handlers
    # ==========================================
    
    async def _handle_scan_link(
        self,
        urls: List[str],
        message: str,
        context: str
    ) -> FormattedResponse:
        """Handle link scanning"""
        self._stats["scans_performed"] += 1
        
        if not urls:
            # Try to extract from message
            urls = self.intent_router.extract_urls(message)
        
        if not urls:
            return FormattedResponse(
                text="Please provide a URL to scan. Just paste the link!",
                intent=Intent.SCAN_LINK,
                confidence=0.5,
                suggested_actions=["Paste a URL", "Get help"]
            )
        
        url = urls[0]  # Scan first URL
        
        # Use tools if available
        if self.tools:
            try:
                scan_result = await self.tools.scan_link(url)
                
                # Get LLM explanation if available
                explanation = None
                if self.llm_router:
                    explanation = await self.llm_router.explain_scan(
                        scan_type="link",
                        scan_result=scan_result,
                        context=context
                    )
                
                return self.response_builder.build_scan_response(
                    scan_type="link",
                    scan_result=scan_result,
                    llm_explanation=explanation
                )
            except Exception as e:
                logger.error(f"Link scan error: {e}")
        
        # Fallback: basic response
        return FormattedResponse(
            text=f"🔍 Analyzing link: {url}\n\nScan tools temporarily unavailable.",
            intent=Intent.SCAN_LINK,
            confidence=0.7,
            suggested_actions=["Try again", "Ask a question"]
        )
    
    async def _handle_scan_email(
        self,
        message: str,
        context: str
    ) -> FormattedResponse:
        """Handle email scanning"""
        self._stats["scans_performed"] += 1
        
        if self.tools:
            try:
                scan_result = await self.tools.scan_email(message)
                
                explanation = None
                if self.llm_router:
                    explanation = await self.llm_router.explain_scan(
                        scan_type="email",
                        scan_result=scan_result,
                        context=context
                    )
                
                return self.response_builder.build_scan_response(
                    scan_type="email",
                    scan_result=scan_result,
                    llm_explanation=explanation
                )
            except Exception as e:
                logger.error(f"Email scan error: {e}")
        
        return FormattedResponse(
            text="📧 Email scan tools temporarily unavailable.",
            intent=Intent.SCAN_EMAIL,
            confidence=0.7,
            suggested_actions=["Try again", "Ask about phishing"]
        )
    
    async def _handle_scan_logs(
        self,
        message: str,
        context: str
    ) -> FormattedResponse:
        """Handle log scanning"""
        self._stats["scans_performed"] += 1
        
        if self.tools:
            try:
                scan_result = await self.tools.scan_logs(message)
                
                explanation = None
                if self.llm_router:
                    explanation = await self.llm_router.explain_scan(
                        scan_type="logs",
                        scan_result=scan_result,
                        context=context
                    )
                
                return self.response_builder.build_scan_response(
                    scan_type="logs",
                    scan_result=scan_result,
                    llm_explanation=explanation
                )
            except Exception as e:
                logger.error(f"Logs scan error: {e}")
        
        return FormattedResponse(
            text="📋 Log scan tools temporarily unavailable.",
            intent=Intent.SCAN_LOGS,
            confidence=0.7,
            suggested_actions=["Try again", "Ask a question"]
        )
    
    async def _handle_status(self) -> FormattedResponse:
        """Handle Guardian status request"""
        status = {
            "status": "healthy",
            "components": {
                "intent_router": "active",
                "memory_manager": "active",
                "response_builder": "active",
                "tools": "active" if self.tools else "not_configured",
                "llm": "active" if self.llm_router else "not_configured"
            },
            "stats": {
                "scans_today": self._stats["scans_performed"],
                "messages_today": self._stats["total_messages"],
                "threats_blocked": 0  # TODO: Track actual threats
            }
        }
        
        return self.response_builder.build_status_response(status)
    
    async def _handle_security_question(
        self,
        message: str,
        context: str
    ) -> FormattedResponse:
        """Handle security-related questions"""
        if self.llm_router:
            try:
                response = await self.llm_router.answer_security_question(
                    question=message,
                    context=context
                )
                
                return self.response_builder.build_chat_response(
                    llm_response=response,
                    intent=Intent.SECURITY_QUESTION,
                    confidence=0.85,
                    context_used=bool(context)
                )
            except Exception as e:
                logger.error(f"LLM error: {e}")
        
        # Fallback response
        return FormattedResponse(
            text="I'd love to answer your security question, but my AI is temporarily offline. Try asking about phishing, malware, or passwords!",
            intent=Intent.SECURITY_QUESTION,
            confidence=0.5,
            suggested_actions=["What is phishing?", "Password tips", "Scan a link"]
        )
    
    async def _handle_general_chat(
        self,
        message: str,
        context: str
    ) -> FormattedResponse:
        """Handle general chat"""
        if self.llm_router:
            try:
                response = await self.llm_router.chat(
                    message=message,
                    context=context
                )
                
                return self.response_builder.build_chat_response(
                    llm_response=response,
                    intent=Intent.GENERAL_CHAT,
                    confidence=0.7,
                    context_used=bool(context)
                )
            except Exception as e:
                logger.error(f"LLM error: {e}")
        
        # Fallback
        return FormattedResponse(
            text="I'm here to help with security! Try asking about phishing, scanning a link, or checking suspicious emails.",
            intent=Intent.GENERAL_CHAT,
            confidence=0.5,
            suggested_actions=["What can you do?", "Scan a link", "Security tips"]
        )
    
    # ==========================================
    # Gateway Status
    # ==========================================
    
    async def get_status(self) -> dict:
        """Get gateway status"""
        return {
            "status": "online",
            "components": {
                "intent_router": "active",
                "memory_manager": "active",
                "response_builder": "active",
                "tools": "configured" if self.tools else "not_configured",
                "llm": "configured" if self.llm_router else "not_configured"
            },
            "stats": self._stats
        }
    
    def get_capabilities(self) -> dict:
        """Get gateway capabilities"""
        return {
            "intents": [i.value for i in Intent],
            "platforms": ["telegram", "web", "mobile", "api"],
            "features": {
                "link_scanning": bool(self.tools),
                "email_scanning": bool(self.tools),
                "log_analysis": bool(self.tools),
                "ai_chat": bool(self.llm_router),
                "cross_platform_memory": True
            }
        }
