"""
Summary Engine - Conversation Compression
For long conversations, compress old context into summaries.
Keeps LLM context window efficient.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from .conversation_store import Conversation, Message


@dataclass
class ConversationSummary:
    """Summarized conversation context."""
    user_id: str
    summary: str
    key_topics: List[str]
    risk_scans_done: List[str]
    user_preferences: Dict[str, Any]
    created_at: datetime
    covers_messages: int  # How many messages this summary covers


class SummaryEngine:
    """
    Conversation Summary Engine.
    
    Compresses long conversation histories into summaries.
    Use this when conversation exceeds context window.
    """
    
    def __init__(self, summary_threshold: int = 20):
        """
        Initialize summary engine.
        
        Args:
            summary_threshold: Create summary after this many messages
        """
        self.summary_threshold = summary_threshold
        self.summaries: Dict[str, ConversationSummary] = {}
    
    def should_summarize(self, conversation: Conversation) -> bool:
        """Check if conversation needs summarization."""
        if not conversation:
            return False
        
        # Already has recent summary
        if conversation.summary:
            return False
        
        return len(conversation.messages) >= self.summary_threshold
    
    def create_summary(self, conversation: Conversation) -> ConversationSummary:
        """
        Create summary of conversation.
        
        For production: Use LLM to generate summary.
        For demo: Rule-based extraction.
        """
        user_id = conversation.user_id
        messages = conversation.messages
        
        # Extract key information
        key_topics = self._extract_topics(messages)
        risk_scans = self._extract_risk_scans(messages)
        preferences = self._extract_preferences(messages)
        
        # Build summary text
        summary_text = self._build_summary_text(
            key_topics, risk_scans, preferences, len(messages)
        )
        
        summary = ConversationSummary(
            user_id=user_id,
            summary=summary_text,
            key_topics=key_topics,
            risk_scans_done=risk_scans,
            user_preferences=preferences,
            created_at=datetime.now(),
            covers_messages=len(messages)
        )
        
        self.summaries[user_id] = summary
        
        return summary
    
    def _extract_topics(self, messages: List[Message]) -> List[str]:
        """Extract main topics from conversation."""
        topics = set()
        topic_keywords = {
            "phishing": ["phishing", "scam", "fake", "suspicious email"],
            "malware": ["malware", "virus", "trojan", "infected"],
            "password_security": ["password", "credentials", "login"],
            "link_scanning": ["link", "url", "website", "check this"],
            "email_scanning": ["email", "invoice", "urgent", "attachment"],
            "logs_analysis": ["logs", "security logs", "incidents", "brute force"],
            "account_security": ["2fa", "mfa", "authentication", "account"],
            "data_breach": ["breach", "leaked", "compromised", "exposed"]
        }
        
        for message in messages:
            content_lower = message.content.lower()
            for topic, keywords in topic_keywords.items():
                if any(kw in content_lower for kw in keywords):
                    topics.add(topic)
        
        return list(topics)
    
    def _extract_risk_scans(self, messages: List[Message]) -> List[str]:
        """Extract what risk scans were performed."""
        scans = []
        
        for message in messages:
            content_lower = message.content.lower()
            
            # Check for tool results
            if message.role.value == "tool":
                scans.append(message.content.split("]")[0].replace("[", ""))
            
            # Check for scan requests
            if any(kw in content_lower for kw in ["check this link", "scan this url", "is this safe"]):
                scans.append("link_scan")
            if any(kw in content_lower for kw in ["check this email", "is this phishing", "suspicious email"]):
                scans.append("email_scan")
            if any(kw in content_lower for kw in ["analyze logs", "security logs", "check logs"]):
                scans.append("logs_scan")
        
        return list(set(scans))
    
    def _extract_preferences(self, messages: List[Message]) -> Dict[str, Any]:
        """Extract user preferences from conversation patterns."""
        preferences = {
            "prefers_detailed_explanations": False,
            "prefers_quick_answers": False,
            "technical_level": "basic",
            "primary_concerns": []
        }
        
        concern_patterns = {
            "business_email": ["business", "work", "company", "corporate"],
            "personal_security": ["personal", "family", "home"],
            "compliance": ["compliance", "audit", "regulation"],
            "training": ["train", "educate", "learn", "explain"]
        }
        
        detailed_requests = 0
        quick_requests = 0
        technical_terms = 0
        
        for message in messages:
            content_lower = message.content.lower()
            
            # Check explanation preferences
            if any(kw in content_lower for kw in ["explain", "why", "how does", "tell me more"]):
                detailed_requests += 1
            if any(kw in content_lower for kw in ["quick", "just tell me", "yes or no"]):
                quick_requests += 1
            
            # Check technical level
            if any(kw in content_lower for kw in ["api", "ssl", "tls", "dns", "header", "spf", "dkim"]):
                technical_terms += 1
            
            # Extract concerns
            for concern, keywords in concern_patterns.items():
                if any(kw in content_lower for kw in keywords):
                    if concern not in preferences["primary_concerns"]:
                        preferences["primary_concerns"].append(concern)
        
        # Set preferences based on patterns
        if detailed_requests > quick_requests:
            preferences["prefers_detailed_explanations"] = True
        if quick_requests > detailed_requests:
            preferences["prefers_quick_answers"] = True
        if technical_terms >= 3:
            preferences["technical_level"] = "advanced"
        elif technical_terms >= 1:
            preferences["technical_level"] = "intermediate"
        
        return preferences
    
    def _build_summary_text(
        self, 
        topics: List[str], 
        scans: List[str], 
        preferences: Dict[str, Any],
        message_count: int
    ) -> str:
        """Build human-readable summary."""
        parts = []
        
        parts.append(f"Conversation with {message_count} messages.")
        
        if topics:
            parts.append(f"Main topics: {', '.join(topics)}.")
        
        if scans:
            parts.append(f"Risk scans performed: {', '.join(set(scans))}.")
        
        if preferences["primary_concerns"]:
            parts.append(f"User concerns: {', '.join(preferences['primary_concerns'])}.")
        
        tech_level = preferences["technical_level"]
        if tech_level != "basic":
            parts.append(f"User appears {tech_level}-level technical.")
        
        if preferences["prefers_detailed_explanations"]:
            parts.append("User prefers detailed explanations.")
        elif preferences["prefers_quick_answers"]:
            parts.append("User prefers quick, concise answers.")
        
        return " ".join(parts)
    
    def get_summary(self, user_id: str) -> Optional[ConversationSummary]:
        """Get existing summary for user."""
        return self.summaries.get(user_id)
    
    def get_context_prompt(self, user_id: str) -> str:
        """
        Get summary as context prompt for LLM.
        
        Use this to inject context at the start of LLM conversation.
        """
        summary = self.get_summary(user_id)
        
        if not summary:
            return ""
        
        return f"""
Previous conversation context:
{summary.summary}

Key topics discussed: {', '.join(summary.key_topics) if summary.key_topics else 'None'}
Risk scans done: {', '.join(summary.risk_scans_done) if summary.risk_scans_done else 'None'}

Continue the conversation with this context in mind.
"""


# Global instance
summary_engine = SummaryEngine()
