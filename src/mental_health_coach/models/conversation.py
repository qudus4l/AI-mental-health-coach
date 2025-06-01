"""Conversation models for the mental health coach application.

This module defines the database models for conversations, messages,
and important memories extracted from conversations.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from src.mental_health_coach.database import Base


class Conversation(Base):
    """Model for storing conversation sessions between users and the AI coach.
    
    Attributes:
        id: Unique identifier for the conversation.
        user_id: ID of the user participating in the conversation.
        title: Optional title for the conversation.
        is_formal_session: Whether this is a formal therapy session.
        session_number: For formal sessions, the sequential session number.
        started_at: When the conversation started.
        ended_at: When the conversation ended (may be null if ongoing).
        summary: Optional AI-generated summary of the conversation.
    """
    
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    is_formal_session = Column(Boolean, default=False, nullable=False)
    session_number = Column(Integer, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    important_memories = relationship("ImportantMemory", back_populates="conversation", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="conversation", cascade="all, delete-orphan")
    mood_rating = relationship("SessionMoodRating", back_populates="conversation", uselist=False, cascade="all, delete-orphan")
    homework_assignments = relationship("HomeworkAssignment", back_populates="conversation", cascade="all, delete-orphan")
    

class Message(Base):
    """Model for storing individual messages within a conversation.
    
    Attributes:
        id: Unique identifier for the message.
        conversation_id: ID of the conversation this message belongs to.
        user_id: ID of the user (may be null for AI messages).
        content: Text content of the message.
        is_from_user: Whether the message is from the user (vs. AI).
        created_at: When the message was created.
        is_transcript: Whether this message is a transcript of speech.
    """
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)
    is_from_user = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_transcript = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User", back_populates="messages")


class ImportantMemory(Base):
    """Model for storing important memories extracted from conversations.
    
    This model stores therapeutically significant insights, patterns,
    or breakthroughs identified in conversations for later reference.
    
    Attributes:
        id: Unique identifier for the memory.
        user_id: ID of the user this memory relates to.
        conversation_id: ID of the conversation this memory was extracted from.
        content: Text content of the memory.
        category: Category of the memory (triggers, coping_strategies, etc.).
        importance_score: AI-assigned importance score (0.0-1.0).
        created_at: When the memory was created.
    """
    
    __tablename__ = "important_memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    importance_score = Column(Float, nullable=False, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="important_memories")
    conversation = relationship("Conversation", back_populates="important_memories") 