"""
Conversation Store - Cross-Platform Memory
Same user recognized everywhere. Telegram, Web, Mobile - ONE conversation history.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import hashlib


class MessageRole(str, Enum):
    """Who sent the message."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class Message:
    """Single message in conversation."""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    platform: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "platform": self.platform,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        """Create from dictionary."""
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            platform=data.get("platform", "unknown"),
            metadata=data.get("metadata", {})
        )


@dataclass
class Conversation:
    """Full conversation with a user."""
    user_id: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    summary: Optional[str] = None
    context_tags: List[str] = field(default_factory=list)
    
    def add_message(self, message: Message):
        """Add message and update activity timestamp."""
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def get_recent(self, limit: int = 10) -> List[Message]:
        """Get recent messages."""
        return self.messages[-limit:]
    
    def get_for_llm(self, limit: int = 10) -> List[Dict]:
        """Get messages formatted for LLM context."""
        recent = self.get_recent(limit)
        return [
            {"role": m.role.value, "content": m.content}
            for m in recent
        ]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "summary": self.summary,
            "context_tags": self.context_tags
        }


class ConversationStore:
    """
    Cross-Platform Conversation Storage.
    
    Same user ID recognized across all platforms.
    User 'john@company.com' on Telegram = Web = Mobile.
    """
    
    def __init__(self, max_messages_per_user: int = 100):
        self.conversations: Dict[str, Conversation] = {}
        self.max_messages = max_messages_per_user
        self.user_platform_map: Dict[str, List[str]] = {}  # Track which platforms each user uses
    
    def _normalize_user_id(self, user_id: str) -> str:
        """
        Normalize user ID across platforms.
        Strips platform prefixes for unified identity.
        """
        prefixes = ["telegram_", "web_", "mobile_", "api_"]
        normalized = user_id.lower().strip()
        
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
                break
        
        return normalized
    
    def _get_or_create(self, user_id: str) -> Conversation:
        """Get existing conversation or create new one."""
        normalized = self._normalize_user_id(user_id)
        
        if normalized not in self.conversations:
            self.conversations[normalized] = Conversation(user_id=normalized)
        
        return self.conversations[normalized]
    
    def add_user_message(
        self, 
        user_id: str, 
        content: str, 
        platform: str = "unknown",
        metadata: Optional[Dict] = None
    ) -> Message:
        """Add a user message."""
        conversation = self._get_or_create(user_id)
        normalized = self._normalize_user_id(user_id)
        
        # Track platform usage
        if normalized not in self.user_platform_map:
            self.user_platform_map[normalized] = []
        if platform not in self.user_platform_map[normalized]:
            self.user_platform_map[normalized].append(platform)
        
        message = Message(
            role=MessageRole.USER,
            content=content,
            platform=platform,
            metadata=metadata or {}
        )
        
        conversation.add_message(message)
        self._trim_if_needed(conversation)
        
        return message
    
    def add_assistant_message(
        self, 
        user_id: str, 
        content: str, 
        platform: str = "unknown",
        metadata: Optional[Dict] = None
    ) -> Message:
        """Add an assistant response."""
        conversation = self._get_or_create(user_id)
        
        message = Message(
            role=MessageRole.ASSISTANT,
            content=content,
            platform=platform,
            metadata=metadata or {}
        )
        
        conversation.add_message(message)
        self._trim_if_needed(conversation)
        
        return message
    
    def add_tool_result(
        self, 
        user_id: str, 
        tool_name: str, 
        result: str,
        metadata: Optional[Dict] = None
    ) -> Message:
        """Add a tool execution result."""
        conversation = self._get_or_create(user_id)
        
        message = Message(
            role=MessageRole.TOOL,
            content=f"[{tool_name}] {result}",
            metadata={"tool": tool_name, **(metadata or {})}
        )
        
        conversation.add_message(message)
        
        return message
    
    def get_conversation(self, user_id: str) -> Optional[Conversation]:
        """Get user's conversation."""
        normalized = self._normalize_user_id(user_id)
        return self.conversations.get(normalized)
    
    def get_history(self, user_id: str, limit: int = 10) -> List[Message]:
        """Get recent conversation history."""
        conversation = self.get_conversation(user_id)
        if not conversation:
            return []
        return conversation.get_recent(limit)
    
    def get_context_for_llm(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation formatted for LLM context window."""
        conversation = self.get_conversation(user_id)
        if not conversation:
            return []
        return conversation.get_for_llm(limit)
    
    def get_user_platforms(self, user_id: str) -> List[str]:
        """Get all platforms a user has interacted from."""
        normalized = self._normalize_user_id(user_id)
        return self.user_platform_map.get(normalized, [])
    
    def set_summary(self, user_id: str, summary: str):
        """Set conversation summary (from summary engine)."""
        conversation = self._get_or_create(user_id)
        conversation.summary = summary
    
    def add_context_tag(self, user_id: str, tag: str):
        """Add a context tag (e.g., 'frequent_link_checker')."""
        conversation = self._get_or_create(user_id)
        if tag not in conversation.context_tags:
            conversation.context_tags.append(tag)
    
    def get_context_tags(self, user_id: str) -> List[str]:
        """Get user's context tags."""
        conversation = self.get_conversation(user_id)
        if not conversation:
            return []
        return conversation.context_tags
    
    def _trim_if_needed(self, conversation: Conversation):
        """Trim old messages if over limit."""
        if len(conversation.messages) > self.max_messages:
            # Keep most recent, discard oldest
            conversation.messages = conversation.messages[-self.max_messages:]
    
    def clear_conversation(self, user_id: str):
        """Clear user's conversation history."""
        normalized = self._normalize_user_id(user_id)
        if normalized in self.conversations:
            del self.conversations[normalized]
    
    def get_stats(self) -> Dict:
        """Get storage statistics."""
        total_messages = sum(
            len(c.messages) for c in self.conversations.values()
        )
        
        return {
            "total_users": len(self.conversations),
            "total_messages": total_messages,
            "users_by_platform": self._count_by_platform()
        }
    
    def _count_by_platform(self) -> Dict[str, int]:
        """Count users by platform."""
        counts: Dict[str, int] = {}
        for platforms in self.user_platform_map.values():
            for platform in platforms:
                counts[platform] = counts.get(platform, 0) + 1
        return counts


# Global instance for easy access
conversation_store = ConversationStore()
