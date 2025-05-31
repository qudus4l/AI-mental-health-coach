"""Tests for the conversation models."""

from typing import TYPE_CHECKING
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from src.mental_health_coach.models.user import User
from src.mental_health_coach.models.conversation import Conversation, Message, ImportantMemory

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def user(db: Session) -> User:
    """Create a test user.
    
    Args:
        db: Database session.
        
    Returns:
        User: Test user.
    """
    user_data = {
        "email": "test@example.com",
        "hashed_password": "hashed_password",
        "first_name": "Test",
        "last_name": "User",
    }
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_create_conversation(db: Session, user: User) -> None:
    """Test creating a conversation.
    
    Args:
        db: Database session.
        user: Test user.
    """
    # Create a conversation
    conversation_data = {
        "user_id": user.id,
        "title": "Test Conversation",
        "is_formal_session": True,
        "session_number": 1,
    }
    conversation = Conversation(**conversation_data)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    # Check the conversation was created with the correct data
    assert conversation.id is not None
    assert conversation.user_id == user.id
    assert conversation.title == conversation_data["title"]
    assert conversation.is_formal_session == conversation_data["is_formal_session"]
    assert conversation.session_number == conversation_data["session_number"]
    assert isinstance(conversation.started_at, datetime)
    assert conversation.ended_at is None
    
    # Check the relationship to the user
    assert conversation.user == user


def test_create_message(db: Session, user: User) -> None:
    """Test creating a message.
    
    Args:
        db: Database session.
        user: Test user.
    """
    # Create a conversation
    conversation = Conversation(user_id=user.id, title="Test Conversation")
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    # Create a message
    message_data = {
        "conversation_id": conversation.id,
        "is_from_user": True,
        "content": "Hello, AI coach!",
    }
    message = Message(**message_data)
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Check the message was created with the correct data
    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.is_from_user == message_data["is_from_user"]
    assert message.content == message_data["content"]
    assert isinstance(message.created_at, datetime)
    
    # Check the relationship to the conversation
    assert message.conversation == conversation
    
    # Check the relationship from the conversation
    assert message in conversation.messages


def test_create_important_memory(db: Session, user: User) -> None:
    """Test creating an important memory.
    
    Args:
        db: Database session.
        user: Test user.
    """
    # Create a conversation and message
    conversation = Conversation(user_id=user.id, title="Test Conversation")
    db.add(conversation)
    db.commit()
    
    message = Message(
        conversation_id=conversation.id,
        is_from_user=True,
        content="I get anxious when speaking in public.",
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Create an important memory
    memory_data = {
        "user_id": user.id,
        "content": "User experiences anxiety with public speaking.",
        "category": "triggers",
        "importance_score": 80,
        "source_message_id": message.id,
    }
    memory = ImportantMemory(**memory_data)
    db.add(memory)
    db.commit()
    db.refresh(memory)
    
    # Check the memory was created with the correct data
    assert memory.id is not None
    assert memory.user_id == user.id
    assert memory.content == memory_data["content"]
    assert memory.category == memory_data["category"]
    assert memory.importance_score == memory_data["importance_score"]
    assert memory.source_message_id == message.id
    assert isinstance(memory.created_at, datetime)
    assert isinstance(memory.updated_at, datetime)
    
    # Check the relationships
    assert memory.user == user
    assert memory.source_message == message
    assert memory in user.important_memories 