"""
Database models for Sentri Retail Demo
Minimal but SaaS-looking schema
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    """User model - staff and HQ IT users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="staff")  # staff, hq_it, admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    scans = relationship("ScanEvent", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")


class ScanEvent(Base):
    """Security scan results"""
    __tablename__ = "scan_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    kind = Column(String, nullable=False)  # link, email, logs, text
    input_preview = Column(String(200), nullable=False)  # Truncated input for display
    risk_score = Column(Integer, default=0)  # 0-100
    risk_level = Column(String, default="LOW")  # LOW, MEDIUM, HIGH
    verdict = Column(String, nullable=False)  # Short verdict text
    explanation = Column(Text)  # Detailed explanation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="scans")


class GuardianSnapshot(Base):
    """Daily Guardian Engine snapshot"""
    __tablename__ = "guardian_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False)
    protection_level = Column(String, default="ACTIVE")  # ACTIVE, WATCH, WARNING
    items_analyzed = Column(Integer, default=0)
    high_risk_blocked = Column(Integer, default=0)
    top_threat = Column(String)  # Top threat description
    summary_text = Column(Text)  # Daily summary text
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Conversation(Base):
    """AI Assistant conversation"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Chat message in a conversation"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class ConversationMemory(Base):
    """Rolling conversation summary for memory layer"""
    __tablename__ = "conversation_memory"
    
    conversation_id = Column(Integer, ForeignKey("conversations.id"), primary_key=True)
    summary = Column(Text, default="")
    topics_covered = Column(Text, default="")  # Comma-separated topics already discussed
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())