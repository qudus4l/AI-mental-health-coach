"""Tests for Phase 3 functionality."""

from typing import TYPE_CHECKING, Dict, Any
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.mental_health_coach.models.user import User, UserProfile, SessionSchedule
from src.mental_health_coach.models.conversation import Conversation, Message
from src.mental_health_coach.auth.security import create_access_token, get_password_hash
from src.mental_health_coach.services.crisis_detection import CrisisDetector

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def user(db: Session) -> User:
    """Create a test user with profile and session schedules.
    
    Args:
        db: Database session.
        
    Returns:
        User: The test user.
    """
    # Create user
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
    
    # Create profile
    profile = UserProfile(
        user_id=user.id,
        age=30,
        location="Test City",
        anxiety_score=5,
        depression_score=3,
        communication_preference="text",
        session_frequency=2,
    )
    db.add(profile)
    db.commit()
    
    # Create session schedules
    schedule1 = SessionSchedule(
        user_id=user.id,
        day_of_week=1,  # Tuesday
        hour=14,
        minute=30,
        is_active=True,
    )
    schedule2 = SessionSchedule(
        user_id=user.id,
        day_of_week=4,  # Friday
        hour=10,
        minute=0,
        is_active=True,
    )
    db.add(schedule1)
    db.add(schedule2)
    db.commit()
    
    return user


@pytest.fixture
def user_token(user: User) -> str:
    """Create a token for the test user.
    
    Args:
        user: The test user.
        
    Returns:
        str: The access token.
    """
    return create_access_token(data={"sub": user.email})


def test_session_schedule_endpoints(client: TestClient, user: User, user_token: str, db: Session) -> None:
    """Test the session schedule endpoints.
    
    Args:
        client: The test client.
        user: The test user.
        user_token: The access token for the test user.
        db: The database session.
    """
    # Test getting session schedules
    response = client.get(
        "/api/users/me/schedule",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["day_of_week"] == 1  # Tuesday
    assert data[1]["day_of_week"] == 4  # Friday
    
    # Test creating a new session schedule
    response = client.post(
        "/api/users/me/schedule",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "day_of_week": 2,  # Wednesday
            "hour": 15,
            "minute": 0,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["day_of_week"] == 2
    assert data["hour"] == 15
    assert data["minute"] == 0
    new_schedule_id = data["id"]
    
    # Test updating a session schedule
    response = client.put(
        f"/api/users/me/schedule/{new_schedule_id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "day_of_week": 3,  # Thursday
            "hour": 16,
            "minute": 30,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["day_of_week"] == 3
    assert data["hour"] == 16
    assert data["minute"] == 30
    
    # Verify in database
    db_schedule = db.query(SessionSchedule).filter(SessionSchedule.id == new_schedule_id).first()
    assert db_schedule is not None
    assert db_schedule.day_of_week == 3
    assert db_schedule.hour == 16
    assert db_schedule.minute == 30
    
    # Test deleting a session schedule
    response = client.delete(
        f"/api/users/me/schedule/{new_schedule_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 204
    
    # Verify in database
    db_schedule = db.query(SessionSchedule).filter(SessionSchedule.id == new_schedule_id).first()
    assert db_schedule is not None
    assert db_schedule.is_active is False


def test_crisis_detection_endpoint(client: TestClient, user: User, user_token: str, db: Session) -> None:
    """Test the crisis detection endpoint.
    
    Args:
        client: The test client.
        user: The test user.
        user_token: The access token for the test user.
        db: The database session.
    """
    # Create a conversation
    conversation = Conversation(
        user_id=user.id,
        title="Test Conversation",
        is_formal_session=False,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    # Test with non-crisis message
    response = client.post(
        f"/api/conversations/{conversation.id}/messages",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "is_from_user": True,
            "content": "I'm feeling okay today, just a bit tired.",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert data["message"]["is_from_user"] is True
    assert data["crisis_info"] is None
    
    # Test with crisis message that explicitly uses keywords from CRISIS_KEYWORDS
    response = client.post(
        f"/api/conversations/{conversation.id}/messages",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "is_from_user": True,
            "content": "I want to kill myself. I don't see any reason to live anymore.",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert data["message"]["is_from_user"] is True
    assert data["crisis_info"] is not None
    assert data["crisis_info"]["is_crisis"] is True
    assert "suicide" in data["crisis_info"]["categories"]
    assert "ai_response" in data["crisis_info"]
    
    # Test crisis analysis endpoint
    response = client.post(
        "/api/crisis/analyze",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "message": "I've been feeling very anxious and can't stop having panic attacks.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_crisis"] is True
    assert "severe_anxiety" in data["categories"]
    assert len(data["resources"]) > 0
    
    # Test crisis resources endpoint
    response = client.get(
        "/api/crisis/resources/suicide",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "National Suicide Prevention Lifeline"


def test_dashboard_endpoints(client: TestClient, user: User, user_token: str, db: Session) -> None:
    """Test the dashboard endpoints.
    
    Args:
        client: The test client.
        user: The test user.
        user_token: The access token for the test user.
        db: The database session.
    """
    # Create a conversation with messages
    conversation = Conversation(
        user_id=user.id,
        title="Test Conversation",
        is_formal_session=True,
        session_number=1,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    # Add messages
    for i in range(5):
        message = Message(
            conversation_id=conversation.id,
            is_from_user=i % 2 == 0,
            content=f"Test message {i}",
        )
        db.add(message)
    db.commit()
    
    # Test dashboard data endpoint
    response = client.get(
        "/api/dashboard/me",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_stats" in data
    assert "homework_stats" in data
    assert "engagement_metrics" in data
    assert "progress_over_time" in data
    assert "upcoming_sessions" in data
    
    # Test session stats endpoint
    response = client.get(
        "/api/dashboard/me/session-stats",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_sessions" in data
    assert "avg_messages_per_session" in data
    
    # Test upcoming sessions endpoint
    response = client.get(
        "/api/dashboard/me/upcoming-sessions",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "day" in data[0]
    assert "time" in data[0]
    assert "days_until" in data[0] 