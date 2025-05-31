"""Tests for the emergency contact service."""

from typing import TYPE_CHECKING
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from src.mental_health_coach.services.emergency_contact import EmergencyContact, EmergencyContactService
from src.mental_health_coach.models.user import User

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def user() -> User:
    """Create a test user.
    
    Returns:
        User: The test user.
    """
    return User(
        id=1,
        email="test@example.com",
        hashed_password="hashed_password",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def db_mock() -> MagicMock:
    """Create a mock database session.
    
    Returns:
        MagicMock: The mock database session.
    """
    mock_db = MagicMock(spec=Session)
    return mock_db


def test_emergency_contact_init() -> None:
    """Test EmergencyContact initialization."""
    # Test initialization with all parameters
    contact = EmergencyContact(
        name="Test Contact",
        relationship="Partner",
        phone="+1234567890",
        email="contact@example.com",
        is_primary=True,
    )
    
    assert contact.name == "Test Contact"
    assert contact.relationship == "Partner"
    assert contact.phone == "+1234567890"
    assert contact.email == "contact@example.com"
    assert contact.is_primary is True
    
    # Test initialization with minimal parameters
    contact_minimal = EmergencyContact(
        name="Minimal Contact",
        relationship="Friend",
    )
    
    assert contact_minimal.name == "Minimal Contact"
    assert contact_minimal.relationship == "Friend"
    assert contact_minimal.phone is None
    assert contact_minimal.email is None
    assert contact_minimal.is_primary is False


def test_get_emergency_contacts(user: User, db_mock: MagicMock) -> None:
    """Test retrieving emergency contacts.
    
    Args:
        user: The test user.
        db_mock: The mock database session.
    """
    # Create service
    service = EmergencyContactService(db=db_mock, user=user)
    
    # Get contacts
    contacts = service.get_emergency_contacts()
    
    # Verify results
    assert isinstance(contacts, list)
    assert len(contacts) > 0
    
    # Check that each contact has the expected fields
    for contact in contacts:
        assert "name" in contact
        assert "relationship" in contact
        assert "phone" in contact or "email" in contact
        assert "is_primary" in contact


def test_add_emergency_contact(user: User, db_mock: MagicMock) -> None:
    """Test adding an emergency contact.
    
    Args:
        user: The test user.
        db_mock: The mock database session.
    """
    # Create service
    service = EmergencyContactService(db=db_mock, user=user)
    
    # Add contact with phone
    contact_phone = service.add_emergency_contact(
        name="Phone Contact",
        relationship="Partner",
        phone="+1234567890",
        is_primary=True,
    )
    
    assert contact_phone["name"] == "Phone Contact"
    assert contact_phone["relationship"] == "Partner"
    assert contact_phone["phone"] == "+1234567890"
    assert contact_phone["email"] is None
    assert contact_phone["is_primary"] is True
    
    # Add contact with email
    contact_email = service.add_emergency_contact(
        name="Email Contact",
        relationship="Friend",
        email="friend@example.com",
    )
    
    assert contact_email["name"] == "Email Contact"
    assert contact_email["relationship"] == "Friend"
    assert contact_email["phone"] is None
    assert contact_email["email"] == "friend@example.com"
    assert contact_email["is_primary"] is False
    
    # Test adding contact without phone or email
    with pytest.raises(ValueError):
        service.add_emergency_contact(
            name="Invalid Contact",
            relationship="Colleague",
        )


def test_send_crisis_notification(user: User, db_mock: MagicMock, capfd: 'CaptureFixture') -> None:
    """Test sending a crisis notification.
    
    Args:
        user: The test user.
        db_mock: The mock database session.
        capfd: Fixture to capture stdout/stderr output.
    """
    # Create service
    service = EmergencyContactService(db=db_mock, user=user)
    
    # Override get_emergency_contacts to return controlled test data
    def mock_get_contacts():
        return [
            {
                "name": "Primary Contact",
                "relationship": "Partner",
                "phone": "+1234567890",
                "email": "primary@example.com",
                "is_primary": True,
            },
            {
                "name": "Secondary Contact",
                "relationship": "Friend",
                "phone": None,
                "email": "secondary@example.com",
                "is_primary": False,
            },
        ]
    
    service.get_emergency_contacts = mock_get_contacts
    
    # Test sending notification with no specific contact (should use primary)
    result = service.send_crisis_notification(
        crisis_level="high",
        message="This is a test crisis notification",
    )
    
    # Check notification was logged to stdout
    out, err = capfd.readouterr()
    assert "EMERGENCY NOTIFICATION: high crisis" in out
    assert "To: Primary Contact (Partner)" in out
    assert "This is a test crisis notification" in out
    
    # Check result
    assert result["status"] == "success"
    assert result["contact"] == "Primary Contact"
    assert result["method"] == "phone"
    assert "timestamp" in result
    
    # Test sending notification to specific contact
    result = service.send_crisis_notification(
        crisis_level="medium",
        message="This is another test notification",
        contact_id="Secondary Contact",
    )
    
    # Check notification was logged to stdout
    out, err = capfd.readouterr()
    assert "EMERGENCY NOTIFICATION: medium crisis" in out
    assert "To: Secondary Contact (Friend)" in out
    assert "This is another test notification" in out
    
    # Check result
    assert result["status"] == "success"
    assert result["contact"] == "Secondary Contact"
    assert result["method"] == "email"
    assert "timestamp" in result
    
    # Test with non-existent contact
    result = service.send_crisis_notification(
        crisis_level="low",
        message="This should fail",
        contact_id="Non-existent Contact",
    )
    
    # Check result for error
    assert result["status"] == "error"
    assert "No emergency contact available" in result["message"]


def test_record_crisis_event(user: User, db_mock: MagicMock) -> None:
    """Test recording a crisis event.
    
    Args:
        user: The test user.
        db_mock: The mock database session.
    """
    # Create service
    service = EmergencyContactService(db=db_mock, user=user)
    
    # Record a crisis event
    event = service.record_crisis_event(
        crisis_level="high",
        conversation_id=1,
        message_id=2,
        action_taken="Notified emergency contact",
    )
    
    # Verify event data
    assert event["user_id"] == user.id
    assert event["crisis_level"] == "high"
    assert event["conversation_id"] == 1
    assert event["message_id"] == 2
    assert event["action_taken"] == "Notified emergency contact"
    assert "timestamp" in event
    assert event["requires_followup"] is True  # high level should require followup
    
    # Test medium level
    event_medium = service.record_crisis_event(
        crisis_level="medium",
        conversation_id=3,
        message_id=4,
        action_taken="Provided resources",
    )
    
    assert event_medium["requires_followup"] is True  # medium level should require followup
    
    # Test low level
    event_low = service.record_crisis_event(
        crisis_level="low",
        conversation_id=5,
        message_id=6,
        action_taken="Provided supportive response",
    )
    
    assert event_low["requires_followup"] is False  # low level should not require followup 