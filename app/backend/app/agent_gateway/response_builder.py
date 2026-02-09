"""
Response Builder
================

Formats responses for different platforms and contexts.

Responsibilities:
- Format tool results with explanations
- Add appropriate actions/buttons
- Handle error responses
- Personalize based on context
"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

from .intent_router import Intent

logger = logging.getLogger(__name__)


@dataclass
class FormattedResponse:
    """Formatted response ready for delivery"""
    text: str
    intent: Intent
    confidence: float = 0.0
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


class ResponseBuilder:
    """
    Response Builder - Formats Responses for Delivery
    
    Takes tool results and LLM output and creates
    polished responses appropriate for each platform.
    """
    
    def __init__(self):
        """Initialize Response Builder"""
        logger.info("🎨 Response Builder initialized")
    
    def build_scan_response(
        self,
        scan_type: str,
        scan_result: dict,
        llm_explanation: str = None,
        platform: str = "web"
    ) -> FormattedResponse:
        """
        Build response for scan results
        
        Args:
            scan_type: Type of scan (link, email, logs)
            scan_result: Result from risk tool
            llm_explanation: Optional LLM-generated explanation
            platform: Target platform
            
        Returns:
            FormattedResponse
        """
        risk_level = scan_result.get("risk_level", "UNKNOWN")
        risk_score = scan_result.get("risk_score", 0)
        verdict = scan_result.get("verdict", "Unable to analyze")
        signals = scan_result.get("signals", [])
        
        # Choose emoji based on risk level
        emoji_map = {
            "CRITICAL": "🚨",
            "HIGH": "⚠️",
            "MEDIUM": "⚡",
            "LOW": "✅",
            "SAFE": "✅",
            "UNKNOWN": "❓"
        }
        emoji = emoji_map.get(risk_level, "❓")
        
        # Build main response
        parts = []
        parts.append(f"{emoji} **{scan_type.upper()} Scan Result**")
        parts.append("")
        parts.append(f"**Risk Level:** {risk_level} ({risk_score}/100)")
        parts.append(f"**Verdict:** {verdict}")
        
        if signals:
            parts.append("")
            parts.append("**Detected Signals:**")
            for signal in signals[:5]:  # Limit to 5
                parts.append(f"• {signal}")
        
        if llm_explanation:
            parts.append("")
            parts.append("**Analysis:**")
            parts.append(llm_explanation)
        
        # Suggested actions based on risk
        actions = self._get_suggested_actions(risk_level, scan_type)
        
        text = "\n".join(parts)
        
        # Map scan_type to intent
        intent_map = {
            "link": Intent.SCAN_LINK,
            "email": Intent.SCAN_EMAIL,
            "logs": Intent.SCAN_LOGS
        }
        intent = intent_map.get(scan_type, Intent.UNKNOWN)
        
        return FormattedResponse(
            text=text,
            intent=intent,
            confidence=0.95,
            suggested_actions=actions,
            metadata={"scan_result": scan_result}
        )
    
    def build_chat_response(
        self,
        llm_response: str,
        intent: Intent,
        confidence: float,
        context_used: bool = False
    ) -> FormattedResponse:
        """
        Build response for chat/Q&A
        
        Args:
            llm_response: Response from LLM
            intent: Detected intent
            confidence: Intent confidence
            context_used: Whether conversation history was used
            
        Returns:
            FormattedResponse
        """
        actions = []
        
        if intent == Intent.SECURITY_QUESTION:
            actions = [
                "Scan a suspicious link",
                "Check an email",
                "Learn more about security"
            ]
        elif intent == Intent.GENERAL_CHAT:
            actions = [
                "Ask security question",
                "Scan a URL",
                "View Guardian status"
            ]
        elif intent == Intent.GREETING:
            actions = [
                "What can you do?",
                "Scan a link",
                "Security tips"
            ]
        
        return FormattedResponse(
            text=llm_response,
            intent=intent,
            confidence=confidence,
            suggested_actions=actions,
            metadata={"context_used": context_used}
        )
    
    def build_status_response(
        self,
        status: dict,
        platform: str = "web"
    ) -> FormattedResponse:
        """
        Build response for status checks
        
        Args:
            status: Guardian status dict
            platform: Target platform
            
        Returns:
            FormattedResponse
        """
        parts = []
        parts.append("🛡️ **Sentri Guardian Status**")
        parts.append("")
        
        # System status
        system_status = status.get("status", "unknown")
        status_emoji = "✅" if system_status == "healthy" else "⚠️"
        parts.append(f"**System:** {status_emoji} {system_status.title()}")
        
        # Component status
        if "components" in status:
            parts.append("")
            parts.append("**Components:**")
            for comp, state in status["components"].items():
                comp_emoji = "✅" if state == "active" else "⚠️"
                parts.append(f"• {comp}: {comp_emoji} {state}")
        
        # Stats
        if "stats" in status:
            parts.append("")
            parts.append("**Today's Activity:**")
            stats = status["stats"]
            parts.append(f"• Scans: {stats.get('scans_today', 0)}")
            parts.append(f"• Threats blocked: {stats.get('threats_blocked', 0)}")
        
        return FormattedResponse(
            text="\n".join(parts),
            intent=Intent.GUARDIAN_STATUS,
            confidence=1.0,
            suggested_actions=["Scan a link", "Check an email", "View logs"],
            metadata={"status": status}
        )
    
    def build_help_response(self, platform: str = "web") -> FormattedResponse:
        """
        Build help response
        
        Args:
            platform: Target platform
            
        Returns:
            FormattedResponse
        """
        text = """🛡️ **Sentri Security Assistant**

I'm your AI-powered security guardian. Here's what I can do:

**🔗 Link Scanning**
Paste any URL and I'll analyze it for threats, phishing, and malware.

**📧 Email Analysis**
Paste suspicious email content and I'll detect phishing attempts.

**📋 Log Review**
Share security logs and I'll identify anomalies and threats.

**💬 Security Q&A**
Ask me anything about cybersecurity, threats, or best practices.

**Commands:**
• Just paste a URL to scan it
• Type "scan email" and paste email content
• Ask any security question
• Say "status" for system status

*I remember our conversations across platforms!*"""

        return FormattedResponse(
            text=text,
            intent=Intent.HELP,
            confidence=1.0,
            suggested_actions=[
                "Scan a suspicious link",
                "What is phishing?",
                "Check system status"
            ]
        )
    
    def build_greeting_response(
        self,
        user_name: str = None,
        platform: str = "web"
    ) -> FormattedResponse:
        """
        Build greeting response
        
        Args:
            user_name: Optional user name
            platform: Target platform
            
        Returns:
            FormattedResponse
        """
        greeting = user_name if user_name else "there"
        
        text = f"""👋 Hello {greeting}!

I'm **Sentri**, your AI security assistant. I'm here to help keep you safe online.

**Quick Actions:**
• Paste any URL to check if it's safe
• Share suspicious emails for analysis
• Ask security questions

How can I help you today?"""

        return FormattedResponse(
            text=text,
            intent=Intent.GREETING,
            confidence=1.0,
            suggested_actions=[
                "Scan a link",
                "What can you do?",
                "Security tips"
            ]
        )
    
    def build_error_response(
        self,
        error_type: str = "general",
        details: str = None
    ) -> FormattedResponse:
        """
        Build error response
        
        Args:
            error_type: Type of error
            details: Optional error details
            
        Returns:
            FormattedResponse
        """
        error_messages = {
            "general": "⚠️ I encountered an issue processing your request. Please try again.",
            "llm_unavailable": "⚠️ My AI brain is temporarily unavailable. I can still scan links and emails using my security tools!",
            "scan_failed": "⚠️ The scan couldn't be completed. Please check the input and try again.",
            "auth_required": "🔐 Please log in to use this feature.",
            "rate_limit": "⏳ Too many requests. Please wait a moment and try again."
        }
        
        text = error_messages.get(error_type, error_messages["general"])
        
        if details:
            text += f"\n\nDetails: {details}"
        
        return FormattedResponse(
            text=text,
            intent=Intent.UNKNOWN,
            confidence=0.0,
            suggested_actions=["Try again", "Get help"],
            metadata={"error_type": error_type}
        )
    
    def _get_suggested_actions(self, risk_level: str, scan_type: str) -> List[str]:
        """Get suggested actions based on scan result"""
        if risk_level in ["CRITICAL", "HIGH"]:
            return [
                "Report this threat",
                "Learn about protection",
                "Scan another item"
            ]
        elif risk_level == "MEDIUM":
            return [
                "Learn more about this",
                "Scan another item",
                "Security tips"
            ]
        else:
            return [
                "Scan another item",
                "Ask a question",
                "View security tips"
            ]
    
    def format_for_platform(
        self,
        response: FormattedResponse,
        platform: str
    ) -> FormattedResponse:
        """
        Apply platform-specific formatting
        
        Args:
            response: Base response
            platform: Target platform
            
        Returns:
            Platform-formatted response
        """
        if platform == "telegram":
            # Telegram uses Markdown
            pass
        elif platform == "web":
            # Web can use HTML or Markdown
            pass
        elif platform == "mobile":
            # Mobile might want shorter text
            if len(response.text) > 500:
                response.text = response.text[:500] + "..."
        
        return response
