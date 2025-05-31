"""Tests for the conversations API endpoints."""

from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.mental_health_coach.auth.security import get_password_hash, create_access_token
from src.mental_health_coach.models.user import User

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
def auth_headers(user_token: str) -> dict:
    """Create authorization headers with the user token.
    
    Args:
        user_token: Access token for the user.
        
    Returns:
        dict: Headers with authorization token.
    """
    return {"Authorization": f"Bearer {user_token}"}


def test_create_conversation(client: TestClient, auth_headers: dict) -> None:
    """Test creating a conversation.
    
    Args:
        client: Test client.
        auth_headers: Headers with authorization token.
    """
    # Test data
    conversation_data = {
        "title": "Test Conversation",
        "is_formal_session": True,
        "session_number": 1,
    }
    
    # Make the request
    response = client.post(
        "/api/conversations/", json=conversation_data, headers=auth_headers
    )
    
    # Check the response
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == conversation_data["title"]
    assert data["is_formal_session"] == conversation_data["is_formal_session"]
    assert data["session_number"] == conversation_data["session_number"]
    assert "id" in data
    assert "user_id" in data
    assert "started_at" in data
    assert "ended_at" in data
    assert data["ended_at"] is None


def test_get_conversations(client: TestClient, auth_headers: dict, db: Session, user: User) -> None:
    """Test getting all conversations for a user.
    
    Args:
        client: Test client.
        auth_headers: Headers with authorization token.
        db: Database session.
        user: Test user.
    """
    # First, create some conversations for the user
    for i in range(3):
        response = client.post(
            "/api/conversations/",
            json={"title": f"Test Conversation {i}"},
            headers=auth_headers,
        )
        assert response.status_code == 201
    
    # Make the request to get all conversations
    response = client.get("/api/conversations/", headers=auth_headers)
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    
    # Check each conversation has the correct fields
    for conversation in data:
        assert "id" in conversation
        assert "user_id" in conversation
        assert conversation["user_id"] == user.id
        assert "title" in conversation
        assert "started_at" in conversation


def test_create_message(client: TestClient, auth_headers: dict) -> None:
    """Test creating a message in a conversation.
    
    Args:
        client: Test client.
        auth_headers: Headers with authorization token.
    """
    # First, create a conversation
    conversation_response = client.post(
        "/api/conversations/", json={"title": "Test Conversation"}, headers=auth_headers
    )
    assert conversation_response.status_code == 201
    conversation_id = conversation_response.json()["id"]
    
    # Test data
    message_data = {
        "is_from_user": True,
        "content": "Hello, AI coach!",
    }
    
    # Make the request
    response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json=message_data,
        headers=auth_headers,
    )
    
    # Check the response
    assert response.status_code == 201
    data = response.json()
    assert data["is_from_user"] == message_data["is_from_user"]
    assert data["content"] == message_data["content"]
    assert data["conversation_id"] == conversation_id
    assert "id" in data
    assert "created_at" in data


def test_create_important_memory(client: TestClient, auth_headers: dict) -> None:
    """Test creating an important memory.
    
    Args:
        client: Test client.
        auth_headers: Headers with authorization token.
    """
    # Test data
    memory_data = {
        "content": "User experiences anxiety with public speaking.",
        "category": "triggers",
        "importance_score": 80,
    }
    
    # Make the request
    response = client.post(
        "/api/conversations/memories", json=memory_data, headers=auth_headers
    )
    
    # Check the response
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == memory_data["content"]
    assert data["category"] == memory_data["category"]
    assert data["importance_score"] == memory_data["importance_score"]
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "updated_at" in data 