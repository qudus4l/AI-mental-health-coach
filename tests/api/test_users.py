"""Tests for the users API endpoints."""

from typing import TYPE_CHECKING, Dict, Any
import json
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.mental_health_coach.auth.security import get_password_hash
from src.mental_health_coach.models.user import User, UserProfile, SessionSchedule
from src.mental_health_coach.auth.security import create_access_token
from src.mental_health_coach.app import app

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the API.
    
    Returns:
        TestClient: The test client.
    """
    return TestClient(app)


@pytest.fixture
def user(db: Session) -> User:
    """Create a test user.
    
    Args:
        db: The database session.
        
    Returns:
        User: The test user.
    """
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
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
        user: The test user.
        
    Returns:
        str: The access token.
    """
    return create_access_token(data={"sub": user.email})


def test_create_user(client: TestClient, db: Session) -> None:
    """Test creating a new user.
    
    Args:
        client: The test client.
        db: The database session.
    """
    response = client.post(
        "/api/users/",
        json={
            "email": "new@example.com",
            "password": "password123",
            "first_name": "New",
            "last_name": "User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["first_name"] == "New"
    assert data["last_name"] == "User"
    assert "id" in data
    
    # Verify user was created in the database
    user = db.query(User).filter(User.email == "new@example.com").first()
    assert user is not None
    assert user.first_name == "New"
    assert user.last_name == "User"


def test_create_user_existing_email(client: TestClient, user: User) -> None:
    """Test creating a user with an existing email.
    
    Args:
        client: Test client.
        user: Existing user.
    """
    # Test data with existing email
    user_data = {
        "email": user.email,  # Same email as existing user
        "password": "password123",
        "first_name": "New",
        "last_name": "User",
    }
    
    # Make the request
    response = client.post("/api/users/", json=user_data)
    
    # Check the response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Email already registered" in data["detail"]


def test_read_current_user(client: TestClient, user: User, user_token: str) -> None:
    """Test reading the current user.
    
    Args:
        client: The test client.
        user: The test user.
        user_token: The access token for the test user.
    """
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user.email
    assert data["first_name"] == user.first_name
    assert data["last_name"] == user.last_name
    assert data["id"] == user.id


def test_read_current_user_no_token(client: TestClient) -> None:
    """Test getting the current user without a token.
    
    Args:
        client: Test client.
    """
    # Make the request without a token
    response = client.get("/api/users/me")
    
    # Check the response
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_create_user_profile(client: TestClient, user: User, user_token: str, db: Session) -> None:
    """Test creating a user profile.
    
    Args:
        client: The test client.
        user: The test user.
        user_token: The access token for the test user.
        db: The database session.
    """
    response = client.post(
        "/api/users/me/profile",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "age": 30,
            "location": "New York",
            "anxiety_score": 5,
            "depression_score": 3,
            "communication_preference": "voice",
            "session_frequency": 3,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["age"] == 30
    assert data["location"] == "New York"
    assert data["anxiety_score"] == 5
    assert data["depression_score"] == 3
    assert data["communication_preference"] == "voice"
    assert data["session_frequency"] == 3
    
    # Verify profile was created in the database
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    assert profile is not None
    assert profile.age == 30
    assert profile.location == "New York"
    assert profile.anxiety_score == 5
    assert profile.depression_score == 3
    assert profile.communication_preference == "voice"
    assert profile.session_frequency == 3


def test_update_user_profile(client: TestClient, user: User, user_token: str, db: Session) -> None:
    """Test updating a user profile.
    
    Args:
        client: The test client.
        user: The test user.
        user_token: The access token for the test user.
        db: The database session.
    """
    # Create a profile first
    profile = UserProfile(
        user_id=user.id,
        age=25,
        location="Boston",
        anxiety_score=4,
        depression_score=2,
        communication_preference="text",
        session_frequency=2,
    )
    db.add(profile)
    db.commit()
    
    # Update the profile
    response = client.put(
        "/api/users/me/profile",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "age": 26,
            "location": "New York",
            "anxiety_score": 3,
            "depression_score": 1,
            "communication_preference": "voice",
            "session_frequency": 3,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["age"] == 26
    assert data["location"] == "New York"
    assert data["anxiety_score"] == 3
    assert data["depression_score"] == 1
    assert data["communication_preference"] == "voice"
    assert data["session_frequency"] == 3
    
    # Verify profile was updated in the database
    db.refresh(profile)
    assert profile.age == 26
    assert profile.location == "New York"
    assert profile.anxiety_score == 3
    assert profile.depression_score == 1
    assert profile.communication_preference == "voice"
    assert profile.session_frequency == 3


def test_create_session_schedule(client: TestClient, user: User, user_token: str, db: Session) -> None:
    """Test creating a session schedule.
    
    Args:
        client: The test client.
        user: The test user.
        user_token: The access token for the test user.
        db: The database session.
    """
    response = client.post(
        "/api/users/me/schedule",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "day_of_week": 1,  # Tuesday
            "hour": 14,  # 2 PM
            "minute": 30,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["day_of_week"] == 1
    assert data["hour"] == 14
    assert data["minute"] == 30
    assert data["is_active"] is True
    assert "id" in data
    
    # Verify schedule was created in the database
    schedule = db.query(SessionSchedule).filter(SessionSchedule.user_id == user.id).first()
    assert schedule is not None
    assert schedule.day_of_week == 1
    assert schedule.hour == 14
    assert schedule.minute == 30
    assert schedule.is_active is True


def test_read_session_schedules(client: TestClient, user: User, user_token: str, db: Session) -> None:
    """Test reading session schedules.
    
    Args:
        client: The test client.
        user: The test user.
        user_token: The access token for the test user.
        db: The database session.
    """
    # Create two schedules
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
    
    response = client.get(
        "/api/users/me/schedule",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Verify the schedules are returned in the correct order
    assert data[0]["day_of_week"] == 1
    assert data[0]["hour"] == 14
    assert data[0]["minute"] == 30
    
    assert data[1]["day_of_week"] == 4
    assert data[1]["hour"] == 10
    assert data[1]["minute"] == 0


def test_update_session_schedule(client: TestClient, user: User, user_token: str, db: Session) -> None:
    """Test updating a session schedule.
    
    Args:
        client: The test client.
        user: The test user.
        user_token: The access token for the test user.
        db: The database session.
    """
    # Create a schedule
    schedule = SessionSchedule(
        user_id=user.id,
        day_of_week=1,  # Tuesday
        hour=14,
        minute=30,
        is_active=True,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    # Update the schedule
    response = client.put(
        f"/api/users/me/schedule/{schedule.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "day_of_week": 2,  # Wednesday
            "hour": 15,
            "minute": 0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["day_of_week"] == 2
    assert data["hour"] == 15
    assert data["minute"] == 0
    
    # Verify schedule was updated in the database
    db.refresh(schedule)
    assert schedule.day_of_week == 2
    assert schedule.hour == 15
    assert schedule.minute == 0


def test_delete_session_schedule(client: TestClient, user: User, user_token: str, db: Session) -> None:
    """Test deleting a session schedule.
    
    Args:
        client: The test client.
        user: The test user.
        user_token: The access token for the test user.
        db: The database session.
    """
    # Create a schedule
    schedule = SessionSchedule(
        user_id=user.id,
        day_of_week=1,  # Tuesday
        hour=14,
        minute=30,
        is_active=True,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    # Delete the schedule
    response = client.delete(
        f"/api/users/me/schedule/{schedule.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 204
    
    # Verify schedule was marked as inactive (soft delete)
    db.refresh(schedule)
    assert schedule.is_active is False 