"""Tests for Phase 4 features."""

from typing import TYPE_CHECKING, Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.mental_health_coach.models.user import User
from src.mental_health_coach.models.conversation import Conversation, Message, ImportantMemory
from src.mental_health_coach.auth.security import get_password_hash, create_access_token

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
    hashed_password = get_password_hash("password123")
    user = User(
        email="test@example.com",
        hashed_password=hashed_password,
        first_name="Test",
        last_name="User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def user_token(user: User) -> str:
    """Create a token for the test user.
    
    Args:
        user: Test user.
        
    Returns:
        str: Access token for the user.
    """
    return create_access_token(data={"sub": user.email})


@pytest.fixture
def auth_headers(user_token: str) -> Dict[str, str]:
    """Create authorization headers with the user token.
    
    Args:
        user_token: Access token for the user.
        
    Returns:
        Dict[str, str]: Headers with authorization token.
    """
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def user_conversation(db: Session, user: User) -> Conversation:
    """Create a test conversation for the user.
    
    Args:
        db: Database session.
        user: The test user.
        
    Returns:
        Conversation: The created conversation.
    """
    conversation = Conversation(
        user_id=user.id,
        title="Test Conversation",
        is_formal_session=True,
        session_number=1,
    )
    db.add(conversation)
    db.commit()
    
    # Add some messages
    messages = [
        Message(
            conversation_id=conversation.id,
            is_from_user=True,
            content="I've been feeling anxious about work lately.",
        ),
        Message(
            conversation_id=conversation.id,
            is_from_user=False,
            content="I understand. Can you tell me more about what's causing your anxiety at work?",
        ),
        Message(
            conversation_id=conversation.id,
            is_from_user=True,
            content="My boss keeps giving me impossible deadlines and I'm worried I'll fail.",
        ),
        Message(
            conversation_id=conversation.id,
            is_from_user=False,
            content="That sounds stressful. Have you tried discussing the deadlines with your boss?",
        ),
    ]
    
    for message in messages:
        db.add(message)
    
    # Add an important memory
    memory = ImportantMemory(
        user_id=user.id,
        content="User experiences work anxiety due to impossible deadlines",
        category="triggers",
        importance_score=0.85,
    )
    db.add(memory)
    
    db.commit()
    db.refresh(conversation)
    return conversation


def test_memory_endpoints(client: TestClient, auth_headers: Dict[str, str], user_conversation: Conversation) -> None:
    """Test the memory endpoints for RAG-based conversation retrieval.
    
    Args:
        client: Test client.
        auth_headers: Authentication headers.
        user_conversation: Test conversation.
    """
    # Test relevant context endpoint
    query = "anxiety at work"
    response = client.get(
        f"/api/memory/relevant-context?query={query}",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:  # There might not be results depending on the vectorization
        assert "text" in data[0]
        assert "metadata" in data[0]
        assert "similarity_score" in data[0]
    
    # Test timeline endpoint
    response = client.get(
        "/api/memory/timeline",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "type" in data[0]
    assert "date" in data[0]
    assert "details" in data[0]
    
    # Test themes endpoint
    response = client.get(
        "/api/memory/themes",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_emergency_contact_endpoints(client: TestClient, auth_headers: Dict[str, str]) -> None:
    """Test the emergency contact endpoints.
    
    Args:
        client: Test client.
        auth_headers: Authentication headers.
    """
    # Test getting emergency contacts
    response = client.get(
        "/api/emergency/contacts",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Test adding an emergency contact
    contact_data = {
        "name": "Emergency Contact",
        "relationship": "Friend",
        "phone": "+1234567890",
        "email": "emergency@example.com",
        "is_primary": True,
    }
    
    response = client.post(
        "/api/emergency/contacts",
        json=contact_data,
        headers=auth_headers,
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == contact_data["name"]
    assert data["relationship"] == contact_data["relationship"]
    assert data["phone"] == contact_data["phone"]
    assert data["email"] == contact_data["email"]
    assert data["is_primary"] == contact_data["is_primary"]
    
    # Test sending a crisis notification
    notification_data = {
        "crisis_level": "medium",
        "message": "User is experiencing a crisis situation.",
    }
    
    response = client.post(
        "/api/emergency/notify",
        json=notification_data,
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "contact" in data
    assert "method" in data
    assert "timestamp" in data
    
    # Test recording a crisis event
    event_data = {
        "crisis_level": "medium",
        "conversation_id": 1,
        "message_id": 1,
        "action_taken": "Provided resources and contacted emergency contact.",
    }
    
    response = client.post(
        "/api/emergency/events",
        json=event_data,
        headers=auth_headers,
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["crisis_level"] == event_data["crisis_level"]
    assert data["conversation_id"] == event_data["conversation_id"]
    assert data["message_id"] == event_data["message_id"]
    assert data["action_taken"] == event_data["action_taken"]
    assert "requires_followup" in data


def test_conversation_context_retrieval(client: TestClient, auth_headers: Dict[str, str], user_conversation: Conversation) -> None:
    """Test conversation-specific context retrieval.
    
    Args:
        client: Test client.
        auth_headers: Authentication headers.
        user_conversation: Test conversation.
    """
    # Test relevant context for a specific conversation
    query = "anxiety"
    response = client.get(
        f"/api/conversations/{user_conversation.id}/relevant-context?query={query}",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Test themes for a specific conversation
    response = client.get(
        f"/api/conversations/{user_conversation.id}/themes",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) 