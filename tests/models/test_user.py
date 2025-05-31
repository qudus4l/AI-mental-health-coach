"""Tests for the user models."""

from typing import TYPE_CHECKING
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from src.mental_health_coach.models.user import User, UserProfile, SessionSchedule

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def user_data() -> dict:
    """Create test user data.
    
    Returns:
        dict: Test user data.
    """
    return {
        "email": "test@example.com",
        "hashed_password": "hashed_password",
        "first_name": "Test",
        "last_name": "User",
    }


def test_create_user(db: Session, user_data: dict) -> None:
    """Test creating a user.
    
    Args:
        db: Database session.
        user_data: Test user data.
    """
    # Create a user
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Check the user was created with the correct data
    assert user.id is not None
    assert user.email == user_data["email"]
    assert user.hashed_password == user_data["hashed_password"]
    assert user.first_name == user_data["first_name"]
    assert user.last_name == user_data["last_name"]
    assert user.is_active is True
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)


def test_create_user_profile(db: Session, user_data: dict) -> None:
    """Test creating a user profile.
    
    Args:
        db: Database session.
        user_data: Test user data.
    """
    # Create a user
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create a profile for the user
    profile_data = {
        "user_id": user.id,
        "age": 30,
        "location": "Test City",
        "anxiety_score": 5,
        "depression_score": 3,
        "communication_preference": "text",
        "session_frequency": 2,
    }
    profile = UserProfile(**profile_data)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    # Check the profile was created with the correct data
    assert profile.id is not None
    assert profile.user_id == user.id
    assert profile.age == profile_data["age"]
    assert profile.location == profile_data["location"]
    assert profile.anxiety_score == profile_data["anxiety_score"]
    assert profile.depression_score == profile_data["depression_score"]
    assert profile.communication_preference == profile_data["communication_preference"]
    assert profile.session_frequency == profile_data["session_frequency"]
    assert isinstance(profile.created_at, datetime)
    assert isinstance(profile.updated_at, datetime)
    
    # Check the relationship to the user
    assert profile.user == user


def test_create_session_schedule(db: Session, user_data: dict) -> None:
    """Test creating a session schedule.
    
    Args:
        db: Database session.
        user_data: Test user data.
    """
    # Create a user
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create a session schedule for the user
    schedule_data = {
        "user_id": user.id,
        "day_of_week": 1,  # Monday
        "hour": 14,  # 2 PM
        "minute": 30,  # 2:30 PM
    }
    schedule = SessionSchedule(**schedule_data)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    # Check the schedule was created with the correct data
    assert schedule.id is not None
    assert schedule.user_id == user.id
    assert schedule.day_of_week == schedule_data["day_of_week"]
    assert schedule.hour == schedule_data["hour"]
    assert schedule.minute == schedule_data["minute"]
    assert schedule.is_active is True
    assert isinstance(schedule.created_at, datetime)
    assert isinstance(schedule.updated_at, datetime)
    
    # Check the relationship to the user
    assert schedule.user == user 