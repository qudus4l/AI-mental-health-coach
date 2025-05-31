"""Database module for the mental health coach application."""

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

# Create database engine with appropriate connect args
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get a database session.
    
    Yields:
        Session: A SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize the database by creating all tables.
    
    This function creates all database tables based on the declared models.
    It imports the models here to avoid circular import issues.
    """
    # Import all models to ensure they're registered with the Base metadata
    # pylint: disable=import-outside-toplevel,unused-import
    from src.mental_health_coach.models.user import User, UserProfile, SessionSchedule
    from src.mental_health_coach.models.conversation import Conversation, Message, ImportantMemory
    from src.mental_health_coach.models.homework import HomeworkAssignment, HomeworkProgressNote
    
    # Create all tables
    Base.metadata.create_all(bind=engine) 