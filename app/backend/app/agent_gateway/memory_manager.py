"""
Memory Manager
==============

Cross-platform conversation memory system.

Key Features:
- User chatting from Telegram today
- Opens Web tomorrow
- Sentri remembers context!

That's the "one brain" experience.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Single memory entry"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    platform: str = "web"
    intent: str = None
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ConversationContext:
    """User's conversation context"""
    user_id: str
    entries: List[MemoryEntry] = field(default_factory=list)
    summary: str = ""
    last_intent: str = None
    last_platform: str = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        now = datetime.utcnow().isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now


class MemoryManager:
    """
    Memory Manager - Cross-Platform Memory System
    
    Handles:
    - Storing conversation history
    - Loading context for LLM
    - Summarizing long conversations
    - Cross-platform memory continuity
    """
    
    def __init__(self, max_entries: int = 20, summary_threshold: int = 15):
        """
        Initialize Memory Manager
        
        Args:
            max_entries: Maximum entries to keep in active memory
            summary_threshold: When to trigger summarization
        """
        self.max_entries = max_entries
        self.summary_threshold = summary_threshold
        
        # In-memory store (replace with database in production)
        self._store: Dict[str, ConversationContext] = {}
        
        logger.info(f"🧠 Memory Manager initialized (max={max_entries})")
    
    def normalize_user_id(self, user_id: str, platform: str) -> str:
        """
        Normalize user ID across platforms
        
        Strips platform prefix if present, then creates unified ID.
        This allows same user on different platforms to share memory.
        
        Args:
            user_id: Original user ID
            platform: Platform name
            
        Returns:
            Normalized user ID
        """
        # Remove existing platform prefixes
        for prefix in ["telegram_", "web_", "mobile_", "api_"]:
            if user_id.startswith(prefix):
                user_id = user_id[len(prefix):]
                break
        
        return f"user_{user_id}"
    
    def load_memory(self, user_id: str, platform: str = "web") -> ConversationContext:
        """
        Load conversation memory for user
        
        Args:
            user_id: User ID
            platform: Current platform
            
        Returns:
            ConversationContext with history
        """
        normalized_id = self.normalize_user_id(user_id, platform)
        
        if normalized_id not in self._store:
            self._store[normalized_id] = ConversationContext(
                user_id=normalized_id,
                last_platform=platform
            )
            logger.info(f"📝 New memory created for {normalized_id}")
        
        context = self._store[normalized_id]
        context.last_platform = platform
        
        return context
    
    def save_memory(
        self,
        user_id: str,
        user_message: str,
        assistant_reply: str,
        platform: str = "web",
        intent: str = None,
        metadata: dict = None
    ) -> None:
        """
        Save conversation turn to memory
        
        Args:
            user_id: User ID
            user_message: User's message
            assistant_reply: Assistant's reply
            platform: Platform
            intent: Detected intent
            metadata: Additional metadata
        """
        normalized_id = self.normalize_user_id(user_id, platform)
        context = self.load_memory(user_id, platform)
        
        now = datetime.utcnow().isoformat()
        
        # Add user message
        user_entry = MemoryEntry(
            role="user",
            content=user_message,
            timestamp=now,
            platform=platform,
            intent=intent,
            metadata=metadata
        )
        context.entries.append(user_entry)
        
        # Add assistant reply
        assistant_entry = MemoryEntry(
            role="assistant",
            content=assistant_reply,
            timestamp=now,
            platform=platform,
            intent=intent
        )
        context.entries.append(assistant_entry)
        
        context.last_intent = intent
        context.last_platform = platform
        context.updated_at = now
        
        # Check if we need to trim/summarize
        if len(context.entries) > self.max_entries:
            self._trim_memory(context)
        
        self._store[normalized_id] = context
        logger.debug(f"💾 Memory saved for {normalized_id} ({len(context.entries)} entries)")
    
    def get_context_for_llm(
        self,
        user_id: str,
        platform: str = "web",
        max_turns: int = 5
    ) -> List[dict]:
        """
        Get conversation context formatted for LLM
        
        Args:
            user_id: User ID
            platform: Current platform
            max_turns: Maximum conversation turns to include
            
        Returns:
            List of message dicts for LLM
        """
        context = self.load_memory(user_id, platform)
        messages = []
        
        # Add summary if exists
        if context.summary:
            messages.append({
                "role": "system",
                "content": f"Previous conversation summary: {context.summary}"
            })
        
        # Get last N turns (each turn = user + assistant)
        recent_entries = context.entries[-(max_turns * 2):]
        
        for entry in recent_entries:
            messages.append({
                "role": entry.role,
                "content": entry.content
            })
        
        return messages
    
    def get_context_string(
        self,
        user_id: str,
        platform: str = "web",
        max_turns: int = 3
    ) -> str:
        """
        Get context as a simple string for prompts
        
        Args:
            user_id: User ID
            platform: Current platform
            max_turns: Maximum turns to include
            
        Returns:
            String summary of recent context
        """
        context = self.load_memory(user_id, platform)
        
        if not context.entries:
            return ""
        
        parts = []
        
        if context.summary:
            parts.append(f"Previous Summary: {context.summary}")
        
        recent = context.entries[-(max_turns * 2):]
        for entry in recent:
            role = "User" if entry.role == "user" else "Sentri"
            parts.append(f"{role}: {entry.content[:200]}")
        
        return "\n".join(parts)
    
    def _trim_memory(self, context: ConversationContext) -> None:
        """
        Trim old entries and create summary
        
        Args:
            context: Conversation context to trim
        """
        # Keep only recent entries
        old_entries = context.entries[:-self.max_entries]
        context.entries = context.entries[-self.max_entries:]
        
        # Create summary from old entries
        if old_entries:
            summary_parts = []
            for entry in old_entries:
                if entry.intent:
                    summary_parts.append(f"[{entry.intent}] {entry.content[:50]}")
            
            if summary_parts:
                context.summary = f"Earlier: {'; '.join(summary_parts[-5:])}"
        
        logger.debug(f"Memory trimmed, new size: {len(context.entries)}")
    
    def clear_memory(self, user_id: str, platform: str = "web") -> None:
        """
        Clear conversation memory for user
        
        Args:
            user_id: User ID
            platform: Platform
        """
        normalized_id = self.normalize_user_id(user_id, platform)
        if normalized_id in self._store:
            del self._store[normalized_id]
            logger.info(f"🗑️ Memory cleared for {normalized_id}")
    
    def get_user_stats(self, user_id: str, platform: str = "web") -> dict:
        """
        Get memory statistics for user
        
        Args:
            user_id: User ID
            platform: Platform
            
        Returns:
            Dict with memory stats
        """
        context = self.load_memory(user_id, platform)
        
        return {
            "user_id": context.user_id,
            "total_entries": len(context.entries),
            "has_summary": bool(context.summary),
            "last_intent": context.last_intent,
            "last_platform": context.last_platform,
            "created_at": context.created_at,
            "updated_at": context.updated_at
        }
    
    # ==========================================
    # Database Integration (Future)
    # ==========================================
    
    async def load_from_db(self, db_session, user_id: str) -> ConversationContext:
        """
        Load memory from database (future implementation)
        
        Args:
            db_session: Database session
            user_id: User ID
            
        Returns:
            ConversationContext from database
        """
        # Future: Load from database
        return self.load_memory(user_id)
    
    async def save_to_db(self, db_session, context: ConversationContext) -> None:
        """
        Save memory to database (future implementation)
        
        Args:
            db_session: Database session
            context: Conversation context to save
        """
        # Future: Save to database
        pass
