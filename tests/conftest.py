"""Pytest configuration for the mental health coach application tests."""

from typing import Any, Generator
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.mental_health_coach.models.base import Base
from src.mental_health_coach.database import get_db
from src.mental_health_coach.app import app


# Create an in-memory SQLite test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a clean database session for a test.
    
    Yields:
        Session: A SQLAlchemy database session.
    """
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new database session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop the database tables
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with the test database.
    
    Args:
        db: Database session.
        
    Yields:
        TestClient: A FastAPI test client.
    """
    # Override the get_db dependency to use the test database
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create the test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Remove the dependency override
    app.dependency_overrides.clear() 