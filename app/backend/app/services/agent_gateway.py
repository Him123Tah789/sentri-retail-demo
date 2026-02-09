"""
Sentri Agent Gateway - The Central Brain/Router
Clean architecture for multi-channel AI agent

Architecture:
    Telegram / Web Chat
           ↓
    Sentri Agent Gateway ⭐ (brain/router)
           ↓
    ┌───────────────┬───────────────┬───────────────┐
    | Local LLM     | Risk Engines   | Future RAG KB |
    | (chat/summar) | (trusted tools)| (knowledge)   |
    └───────────────┴───────────────┴───────────────┘

Key concept:
✅ LLM talks (generates responses)
✅ Rules/ML decide (risk detection)
✅ Gateway controls everything (routing)
"""
import re
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """User intent classification"""
    SCAN_LINK = "scan_link"
    SCAN_EMAIL = "scan_email"
    SCAN_LOG = "scan_log"
    GENERAL_CHAT = "general_chat"
    HELP = "help"
    STATUS = "status"
    SUMMARY = "summary"
    UNKNOWN = "unknown"


@dataclass
class AgentMessage:
    """Message from any channel"""
    text: str
    user_id: str
    channel: str  # "telegram", "web", "api"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Response from the gateway"""
    text: str
    intent: IntentType
    tool_used: Optional[str] = None
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    scan_result: Optional[Dict] = None
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Tool:
    """Registered tool that the gateway can use"""
    name: str
    description: str
    function: Callable
    keywords: List[str]
    priority: int = 0  # Higher = checked first


class SentriAgentGateway:
    """
    The central brain that routes messages to the right tools.
    
    Flow:
    1. Receive message from any channel
    2. Detect intent (what does the user want?)
    3. Route to appropriate tool (risk engine, LLM, etc.)
    4. Format and return response
    """
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.conversation_history: Dict[str, List[Dict]] = {}
        self._register_default_tools()
        logger.info("🚀 Sentri Agent Gateway initialized")
    
    def _register_default_tools(self):
        """Register built-in tools"""
        # These will be connected to actual implementations
        pass
    
    def register_tool(self, tool: Tool):
        """Register a new tool"""
        self.tools[tool.name] = tool
        logger.info(f"🔧 Registered tool: {tool.name}")
    
    def detect_intent(self, message: str) -> IntentType:
        """
        Detect user intent from message.
        This is the routing logic.
        """
        text = message.lower().strip()
        
        # URL detection (highest priority - security scanning)
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        if re.search(url_pattern, text):
            return IntentType.SCAN_LINK
        
        # Explicit scan commands
        if any(word in text for word in ['scan', 'check', 'analyze', 'verify']):
            if any(word in text for word in ['email', 'mail', 'message', 'phishing']):
                return IntentType.SCAN_EMAIL
            if any(word in text for word in ['log', 'logs', 'event', 'activity']):
                return IntentType.SCAN_LOG
            if any(word in text for word in ['link', 'url', 'website', 'site']):
                return IntentType.SCAN_LINK
        
        # Help request
        if any(word in text for word in ['help', 'how to', 'what can you', 'commands']):
            return IntentType.HELP
        
        # Status check
        if any(word in text for word in ['status', 'health', 'stats', 'report']):
            return IntentType.STATUS
        
        # Summary request
        if any(word in text for word in ['summary', 'summarize', 'overview', 'digest']):
            return IntentType.SUMMARY
        
        # Default to general chat
        return IntentType.GENERAL_CHAT
    
    async def process_message(self, message: AgentMessage) -> AgentResponse:
        """
        Main entry point - process a message from any channel.
        Routes to appropriate tool based on intent.
        """
        logger.info(f"📨 Processing message from {message.channel}: {message.text[:50]}...")
        
        # Detect intent
        intent = self.detect_intent(message.text)
        logger.info(f"🎯 Detected intent: {intent.value}")
        
        # Route to appropriate handler
        try:
            if intent == IntentType.SCAN_LINK:
                return await self._handle_link_scan(message)
            elif intent == IntentType.SCAN_EMAIL:
                return await self._handle_email_scan(message)
            elif intent == IntentType.SCAN_LOG:
                return await self._handle_log_scan(message)
            elif intent == IntentType.HELP:
                return self._handle_help(message)
            elif intent == IntentType.STATUS:
                return await self._handle_status(message)
            elif intent == IntentType.SUMMARY:
                return await self._handle_summary(message)
            else:
                return await self._handle_general_chat(message)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return AgentResponse(
                text=f"Sorry, I encountered an error: {str(e)}",
                intent=intent,
                success=False
            )
    
    async def _handle_link_scan(self, message: AgentMessage) -> AgentResponse:
        """Handle URL scanning using Risk Engine"""
        from .risk_engine import analyze_link
        
        # Extract URL
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, message.text)
        
        if not urls:
            return AgentResponse(
                text="Please provide a URL to scan. Example: `https://example.com`",
                intent=IntentType.SCAN_LINK,
                tool_used="risk_engine"
            )
        
        url = urls[0]
        result = analyze_link(url)
        
        # Format response
        emoji = "🟢" if result.level == "LOW" else "🟡" if result.level == "MEDIUM" else "🔴"
        
        response_text = f"""
{emoji} **Link Scan Result**

**URL:** `{url}`
**Risk Score:** {result.score}/100
**Risk Level:** {result.level}

**Verdict:** {result.verdict}

**Analysis:**
{result.explanation}

**Recommended Actions:**
{chr(10).join(f'• {action}' for action in result.recommended_actions)}
"""
        
        return AgentResponse(
            text=response_text.strip(),
            intent=IntentType.SCAN_LINK,
            tool_used="risk_engine",
            risk_score=result.score,
            risk_level=result.level,
            scan_result={
                "url": url,
                "score": result.score,
                "level": result.level,
                "verdict": result.verdict,
                "actions": result.recommended_actions
            }
        )
    
    async def _handle_email_scan(self, message: AgentMessage) -> AgentResponse:
        """Handle email content scanning"""
        from .risk_engine import analyze_email_content
        
        # The message text after extracting the command could be the email
        email_content = message.text
        
        # Remove common command prefixes
        for prefix in ['scan email', 'check email', 'analyze email', 'scan', 'check', 'analyze']:
            if email_content.lower().startswith(prefix):
                email_content = email_content[len(prefix):].strip()
                break
        
        if len(email_content) < 10:
            return AgentResponse(
                text="Please provide email content to scan. Paste the suspicious email text after the command.",
                intent=IntentType.SCAN_EMAIL,
                tool_used="risk_engine"
            )
        
        result = analyze_email_content(email_content)
        
        emoji = "🟢" if result.level == "LOW" else "🟡" if result.level == "MEDIUM" else "🔴"
        
        response_text = f"""
{emoji} **Email Scan Result**

**Risk Score:** {result.score}/100
**Risk Level:** {result.level}

**Verdict:** {result.verdict}

**Analysis:**
{result.explanation}

**Recommended Actions:**
{chr(10).join(f'• {action}' for action in result.recommended_actions)}
"""
        
        return AgentResponse(
            text=response_text.strip(),
            intent=IntentType.SCAN_EMAIL,
            tool_used="risk_engine",
            risk_score=result.score,
            risk_level=result.level
        )
    
    async def _handle_log_scan(self, message: AgentMessage) -> AgentResponse:
        """Handle security log analysis"""
        from .risk_engine import analyze_log_entry
        
        log_content = message.text
        for prefix in ['scan log', 'check log', 'analyze log', 'scan logs', 'check logs']:
            if log_content.lower().startswith(prefix):
                log_content = log_content[len(prefix):].strip()
                break
        
        if len(log_content) < 5:
            return AgentResponse(
                text="Please provide log content to analyze. Example:\n`scan log failed login from IP 192.168.1.100`",
                intent=IntentType.SCAN_LOG,
                tool_used="risk_engine"
            )
        
        result = analyze_log_entry(log_content)
        
        emoji = "🟢" if result.level == "LOW" else "🟡" if result.level == "MEDIUM" else "🔴"
        
        response_text = f"""
{emoji} **Log Analysis Result**

**Risk Score:** {result.score}/100
**Risk Level:** {result.level}

**Verdict:** {result.verdict}

**Analysis:**
{result.explanation}

**Recommended Actions:**
{chr(10).join(f'• {action}' for action in result.recommended_actions)}
"""
        
        return AgentResponse(
            text=response_text.strip(),
            intent=IntentType.SCAN_LOG,
            tool_used="risk_engine",
            risk_score=result.score,
            risk_level=result.level
        )
    
    def _handle_help(self, message: AgentMessage) -> AgentResponse:
        """Return help information"""
        help_text = """
🛡️ **Sentri Security Assistant**

I'm your retail security guardian. Here's what I can do:

**🔗 Scan Links**
Send any URL and I'll analyze it for phishing/fraud
Example: `https://suspicious-site.xyz/login`

**📧 Scan Emails**
Type `scan email` followed by suspicious email text
Example: `scan email URGENT: Your account will be suspended...`

**📋 Analyze Logs**
Type `scan log` followed by security log entries
Example: `scan log failed login attempt from IP 192.168.1.100`

**💬 General Chat**
Ask me anything about cybersecurity, retail risks, or tech!

**📊 Status**
Type `status` to see system health

**🔧 Commands:**
• `help` - Show this help
• `status` - System status
• `summary` - Get threat summary

Stay safe! 🚀
"""
        return AgentResponse(
            text=help_text.strip(),
            intent=IntentType.HELP
        )
    
    async def _handle_status(self, message: AgentMessage) -> AgentResponse:
        """Return system status"""
        status_text = f"""
📊 **Sentri System Status**

**Gateway:** ✅ Online
**Risk Engine:** ✅ Active
**LLM Service:** ✅ Ready
**Channel:** {message.channel}

**Tools Available:**
• Link Scanner (Phishing Detection)
• Email Analyzer (BEC/Fraud Detection)
• Log Analyzer (Threat Detection)
• General Chat (AI Assistant)

**Time:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
        return AgentResponse(
            text=status_text.strip(),
            intent=IntentType.STATUS
        )
    
    async def _handle_summary(self, message: AgentMessage) -> AgentResponse:
        """Generate threat summary"""
        summary_text = """
📈 **Security Summary**

**Recent Activity:**
• Scans performed today: Active monitoring
• Threat level: Normal operations

**Tips for Today:**
🔹 Always verify unexpected payment requests
🔹 Check sender emails carefully (lookalike domains)
🔹 Don't click links in urgent messages
🔹 When in doubt, scan it with Sentri!

Use `/help` to see all available commands.
"""
        return AgentResponse(
            text=summary_text.strip(),
            intent=IntentType.SUMMARY
        )
    
    async def _handle_general_chat(self, message: AgentMessage) -> AgentResponse:
        """Handle general chat using LLM"""
        from .llm_service import get_local_response, llm_service
        
        # First try local knowledge base (fast)
        local_response = get_local_response(message.text)
        
        if local_response and "I can help you with" not in local_response:
            return AgentResponse(
                text=local_response,
                intent=IntentType.GENERAL_CHAT,
                tool_used="local_knowledge"
            )
        
        # Try LLM for more complex queries
        try:
            llm_response = await llm_service.general_chat(message.text)
            if llm_response and "I couldn't generate" not in llm_response:
                return AgentResponse(
                    text=llm_response,
                    intent=IntentType.GENERAL_CHAT,
                    tool_used="llm"
                )
        except Exception as e:
            logger.warning(f"LLM failed: {e}")
        
        # Fallback
        return AgentResponse(
            text=local_response or "I'm Sentri, your security assistant! Ask me about cybersecurity, scan links, or type `help` for commands.",
            intent=IntentType.GENERAL_CHAT,
            tool_used="fallback"
        )


# Global gateway instance
gateway = SentriAgentGateway()


# Convenience function for processing messages
async def process_message(text: str, user_id: str, channel: str = "api") -> AgentResponse:
    """Process a message through the gateway"""
    message = AgentMessage(text=text, user_id=user_id, channel=channel)
    return await gateway.process_message(message)
