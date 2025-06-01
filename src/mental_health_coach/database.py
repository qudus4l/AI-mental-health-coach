"""Database module for the mental health coach application.

This module provides the database session and base model class.
"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from dotenv import load_dotenv

from src.mental_health_coach.models.base import Base

# Load environment variables
load_dotenv()

# Get database URL from environment or use default SQLite database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mental_health_coach.db")

# For PostgreSQL, make sure the URL starts with postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get a database session.
    
    Yields:
        A database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize the database.
    
    This function creates all tables in the database.
    It imports the models here to avoid circular import issues.
    """
    # Import all models to ensure they're registered with the Base metadata
    # pylint: disable=import-outside-toplevel,unused-import
    # Import User first since other models depend on it
    from src.mental_health_coach.models.user import User, UserProfile, SessionSchedule
    # Then import models that reference User
    from src.mental_health_coach.models.conversation import Conversation, Message, ImportantMemory
    from src.mental_health_coach.models.homework import HomeworkAssignment
    from src.mental_health_coach.models.assessment import Assessment, SessionMoodRating
    from src.mental_health_coach.models.emergency_contact import EmergencyContact
    
    # Create all tables
    Base.metadata.create_all(bind=engine) 