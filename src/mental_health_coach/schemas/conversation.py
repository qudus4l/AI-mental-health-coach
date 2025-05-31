"""Pydantic schemas for conversation-related operations."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class MessageBase(BaseModel):
    """Base schema for message data.
    
    Attributes:
        is_from_user: Flag indicating if the message is from the user (vs AI).
        content: The text content of the message.
    """
    
    is_from_user: bool = Field(..., description="Whether the message is from the user or not")
    content: str = Field(..., description="Content of the message")


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    
    pass


class Message(MessageBase):
    """Schema for message data.
    
    Attributes:
        id: Primary key for the message.
        conversation_id: Foreign key reference to the associated conversation.
        created_at: Timestamp when the message was created.
        updated_at: Timestamp when the message was last updated.
    """
    
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID of the message")
    conversation_id: int = Field(..., description="ID of the conversation")
    created_at: datetime = Field(..., description="When the message was created")
    updated_at: datetime = Field(..., description="When the message was last updated")


class ConversationBase(BaseModel):
    """Base schema for conversation data.
    
    Attributes:
        title: Auto-generated title summarizing the conversation.
        is_formal_session: Flag indicating if this is a formal therapy session.
        session_number: For formal sessions, tracks the sequential number.
    """
    
    title: str = Field(..., description="Title of the conversation")
    is_formal_session: bool = Field(
        False, description="Whether this is a formal therapy session"
    )
    session_number: Optional[int] = Field(
        None, description="Session number (only for formal sessions)"
    )


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation."""
    
    pass


class Conversation(ConversationBase):
    """Schema for conversation data.
    
    Attributes:
        id: Primary key for the conversation.
        user_id: Foreign key reference to the associated user.
        started_at: Timestamp when the conversation started.
        ended_at: Timestamp when the conversation ended.
        messages: List of messages in this conversation.
    """
    
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID of the conversation")
    user_id: int = Field(..., description="ID of the user")
    started_at: datetime = Field(..., description="When the conversation started")
    ended_at: Optional[datetime] = Field(None, description="When the conversation ended")
    messages: List[Message] = Field([], description="Messages in the conversation")


class ImportantMemoryBase(BaseModel):
    """Base schema for important memory data.
    
    Attributes:
        content: The text content of the memory.
        category: The category of memory (triggers, coping_strategies, etc.).
        importance_score: AI-assigned importance score (0-100).
    """
    
    content: str = Field(..., description="Content of the memory")
    category: Optional[str] = Field(None, description="Category of the memory")
    importance_score: int


class ImportantMemoryCreate(ImportantMemoryBase):
    """Schema for creating a new important memory.
    
    Attributes:
        source_message_id: Optional reference to the message that led to this memory.
    """
    
    source_message_id: Optional[int] = None


class ImportantMemory(ImportantMemoryBase):
    """Schema for important memory data.
    
    Attributes:
        id: Primary key for the important memory.
        user_id: Foreign key reference to the associated user.
        source_message_id: Optional reference to the message that led to this memory.
        created_at: Timestamp when the memory was created.
        updated_at: Timestamp when the memory was last updated.
    """
    
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID of the memory")
    user_id: int = Field(..., description="ID of the user")
    source_message_id: Optional[int] = None
    created_at: datetime = Field(..., description="When the memory was created")
    updated_at: datetime = Field(..., description="When the memory was last updated") 