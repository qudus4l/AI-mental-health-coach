"""Tests for the dashboard service."""

from typing import TYPE_CHECKING
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from src.mental_health_coach.services.dashboard import DashboardService
from src.mental_health_coach.models.user import User, SessionSchedule
from src.mental_health_coach.models.conversation import Conversation, Message
from src.mental_health_coach.models.homework import HomeworkAssignment

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
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.join.return_value = mock_query
    mock_query.group_by.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    
    return mock_db


def test_get_dashboard_data(user: User, db_mock: MagicMock) -> None:
    """Test getting the complete dashboard data.
    
    Args:
        user: The test user.
        db_mock: The mock database session.
    """
    # Create dashboard service with mocked db
    service = DashboardService(db=db_mock, user=user)
    
    # Mock the individual data methods
    service.get_session_stats = MagicMock(return_value={"total_sessions": 5})
    service.get_homework_stats = MagicMock(return_value={"completion_rate": 75})
    service.get_engagement_metrics = MagicMock(return_value={"total_messages": 100})
    service.get_progress_over_time = MagicMock(return_value={"weekly_data": []})
    service.get_upcoming_sessions = MagicMock(return_value=[])
    
    # Get dashboard data
    dashboard = service.get_dashboard_data()
    
    # Verify all methods were called
    service.get_session_stats.assert_called_once()
    service.get_homework_stats.assert_called_once()
    service.get_engagement_metrics.assert_called_once()
    service.get_progress_over_time.assert_called_once()
    service.get_upcoming_sessions.assert_called_once()
    
    # Verify dashboard contains all data
    assert "session_stats" in dashboard
    assert dashboard["session_stats"]["total_sessions"] == 5
    
    assert "homework_stats" in dashboard
    assert dashboard["homework_stats"]["completion_rate"] == 75
    
    assert "engagement_metrics" in dashboard
    assert dashboard["engagement_metrics"]["total_messages"] == 100
    
    assert "progress_over_time" in dashboard
    assert "weekly_data" in dashboard["progress_over_time"]
    
    assert "upcoming_sessions" in dashboard
    assert "last_updated" in dashboard


def test_get_session_stats(user: User, db_mock: MagicMock) -> None:
    """Test getting session statistics.
    
    Args:
        user: The test user.
        db_mock: The mock database session.
    """
    # Set up mock query results
    mock_query = db_mock.query.return_value
    
    # Mock all the necessary scalar calls
    mock_query.scalar.side_effect = [
        3,   # total_sessions
        15,  # total_messages
        0,   # total_duration_minutes
    ]
    
    # Mock session message counts
    mock_query.all.side_effect = [
        [(1, 10), (2, 15), (3, 20)],  # session_message_counts
        [],  # sessions_with_duration (empty to test default)
    ]
    
    # Create dashboard service
    service = DashboardService(db=db_mock, user=user)
    
    # Mock the _get_last_session_date method
    last_session_date = datetime.utcnow() - timedelta(days=3)
    service._get_last_session_date = MagicMock(return_value=last_session_date)
    
    # Get session stats
    stats = service.get_session_stats()
    
    # Verify stats
    assert stats["total_sessions"] == 3
    assert stats["avg_messages_per_session"] == 15  # (10 + 15 + 20) / 3
    assert stats["avg_session_duration_minutes"] == 0  # default when no sessions with duration
    assert stats["last_session_date"] == last_session_date


def test_get_homework_stats(user: User, db_mock: MagicMock) -> None:
    """Test getting homework statistics.
    
    Args:
        user: The test user.
        db_mock: The mock database session.
    """
    # Set up mock query results
    mock_query = db_mock.query.return_value
    
    # Mock query scalars
    mock_query.scalar.side_effect = [
        10,  # total_assignments
        8,   # completed_assignments
        1,   # current_assignments
        1,   # overdue_assignments
    ]
    
    # Mock completed homework with completion times
    now = datetime.utcnow()
    
    hw1 = HomeworkAssignment(
        created_at=now - timedelta(days=5),
        completion_date=now - timedelta(days=3),
    )
    
    hw2 = HomeworkAssignment(
        created_at=now - timedelta(days=10),
        completion_date=now - timedelta(days=7),
    )
    
    mock_query.all.return_value = [hw1, hw2]
    
    # Create dashboard service
    service = DashboardService(db=db_mock, user=user)
    
    # Get homework stats
    stats = service.get_homework_stats()
    
    # Verify stats
    assert stats["total_assignments"] == 10
    assert stats["completed_assignments"] == 8
    assert stats["completion_rate"] == 80  # (8 / 10) * 100
    assert stats["current_assignments"] == 1
    assert stats["overdue_assignments"] == 1
    assert stats["avg_days_to_complete"] == 2.5  # (2 + 3) / 2


def test_get_upcoming_sessions(user: User, db_mock: MagicMock) -> None:
    """Test getting upcoming sessions.
    
    Args:
        user: The test user.
        db_mock: The mock database session.
    """
    # Set up mock query results
    mock_query = db_mock.query.return_value
    
    # Mock today's date for predictable testing
    today = datetime(2023, 5, 1)  # A Monday
    
    # Create a session schedule for Wednesday (day_of_week = 2)
    schedule = SessionSchedule(
        user_id=user.id,
        day_of_week=2,
        hour=14,
        minute=30,
        is_active=True,
    )
    
    mock_query.all.return_value = [schedule]
    
    # Create dashboard service
    service = DashboardService(db=db_mock, user=user)
    
    # Mock datetime.utcnow to return our fixed date
    with patch('src.mental_health_coach.services.dashboard.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = today
        mock_datetime.combine.side_effect = datetime.combine
        mock_datetime.min.time.return_value = datetime.min.time()
        
        # Get upcoming sessions
        upcoming = service.get_upcoming_sessions()
    
    # Verify upcoming sessions
    assert len(upcoming) == 1
    assert upcoming[0]["day"] == "Wednesday"
    assert upcoming[0]["time"] == "14:30"
    assert upcoming[0]["days_until"] == 2  # Wednesday is 2 days after Monday 