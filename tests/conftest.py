"""Test configuration for pytest.

This module provides fixtures for testing the mental health coach application.
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import the Base from models.base to ensure consistency
from src.mental_health_coach.models.base import Base
# Import models to ensure they're registered with Base
from src.mental_health_coach.models.user import User, UserProfile, SessionSchedule
from src.mental_health_coach.models.conversation import Conversation, Message, ImportantMemory
from src.mental_health_coach.models.homework import HomeworkAssignment
from src.mental_health_coach.models.assessment import Assessment, SessionMoodRating
from src.mental_health_coach.models.emergency_contact import EmergencyContact


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine.
    
    Returns:
        SQLAlchemy engine for the test database.
    """
    # Use file-based SQLite for tests
    test_db_path = "test_mental_health_coach.db"
    
    # Remove existing test DB if it exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    engine = create_engine(
        f"sqlite:///{test_db_path}",
        connect_args={"check_same_thread": False},
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Clean up after tests
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def db_session(test_db_engine):
    """Create a test database session.
    
    Args:
        test_db_engine: Test database engine.
        
    Returns:
        Database session for testing.
    """
    # Create session
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close() 