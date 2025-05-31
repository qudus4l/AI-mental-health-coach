"""Conversation models for the mental health coach application."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from src.mental_health_coach.models.base import Base


class Conversation(Base):
    """Conversation model representing a complete interaction session.
    
    A conversation is a container for multiple messages exchanged between
    the user and the AI coach during a single interaction.
    
    Attributes:
        id: Primary key for the conversation.
        user_id: Foreign key reference to the associated user.
        title: Auto-generated title summarizing the conversation.
        is_formal_session: Flag indicating if this is a formal therapy session.
        session_number: For formal sessions, tracks the sequential number.
        started_at: Timestamp when the conversation started.
        ended_at: Timestamp when the conversation ended.
        user: Reference to the associated User object.
        messages: List of messages in this conversation.
    """
    
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=True)
    is_formal_session = Column(Boolean, default=False)
    session_number = Column(Integer, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    homework_assignments = relationship("HomeworkAssignment", back_populates="conversation")


class Message(Base):
    """Message model representing a single message in a conversation.
    
    Messages can be from either the user or the AI coach and are always
    part of a conversation.
    
    Attributes:
        id: Primary key for the message.
        conversation_id: Foreign key reference to the associated conversation.
        is_from_user: Flag indicating if the message is from the user (vs AI).
        content: The text content of the message.
        created_at: Timestamp when the message was created.
        updated_at: Timestamp when the message was last updated.
        conversation: Reference to the associated Conversation object.
    """
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    is_from_user = Column(Boolean)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class ImportantMemory(Base):
    """Important memory model for storing key therapeutic insights.
    
    Important memories are AI-curated, significant pieces of information
    about the user that should be remembered across sessions.
    
    Attributes:
        id: Primary key for the important memory.
        user_id: Foreign key reference to the associated user.
        content: The text content of the memory.
        category: The category of memory (triggers, coping_strategies, etc.).
        importance_score: AI-assigned importance score (0.0-1.0).
        source_message_id: Optional reference to the message that led to this memory.
        created_at: Timestamp when the memory was created.
        updated_at: Timestamp when the memory was last updated.
        user: Reference to the associated User object.
    """
    
    __tablename__ = "important_memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    category = Column(String)  # triggers, coping_strategies, breakthrough, goal, etc.
    importance_score = Column(Integer)  # 0-100
    source_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="important_memories")
    source_message = relationship("Message") 