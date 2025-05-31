"""Tests for the authentication API endpoints."""

from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.mental_health_coach.auth.security import get_password_hash
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
    # Create user with known password
    password = "password123"
    hashed_password = get_password_hash(password)
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


def test_login_valid_credentials(client: TestClient, user: User) -> None:
    """Test logging in with valid credentials.
    
    Args:
        client: Test client.
        user: Test user.
    """
    # Form data for login
    login_data = {
        "username": user.email,  # OAuth2 uses "username" field
        "password": "password123",
    }
    
    # Make the request
    response = client.post("/api/auth/token", data=login_data)
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_email(client: TestClient, user: User) -> None:
    """Test logging in with an invalid email.
    
    Args:
        client: Test client.
        user: Test user.
    """
    # Form data with invalid email
    login_data = {
        "username": "wrong@example.com",
        "password": "password123",
    }
    
    # Make the request
    response = client.post("/api/auth/token", data=login_data)
    
    # Check the response
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "Incorrect email or password" in data["detail"]


def test_login_invalid_password(client: TestClient, user: User) -> None:
    """Test logging in with an invalid password.
    
    Args:
        client: Test client.
        user: Test user.
    """
    # Form data with invalid password
    login_data = {
        "username": user.email,
        "password": "wrongpassword",
    }
    
    # Make the request
    response = client.post("/api/auth/token", data=login_data)
    
    # Check the response
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "Incorrect email or password" in data["detail"] 