"""Database module for the mental health coach application.

This module provides the database session and base model class.
"""

import os
import logging
from typing import Generator
import sqlite3

from sqlalchemy import create_engine, inspect, MetaData, Table, Column, Boolean, Text, text
from sqlalchemy.orm import sessionmaker, Session

from dotenv import load_dotenv

from src.mental_health_coach.models.base import Base

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment or use default SQLite database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mental_health_coach.db")
DATABASE_PATH = DATABASE_URL.replace("sqlite:///", "")

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


def check_and_update_schema() -> None:
    """Check and update database schema to match current models.
    
    This function checks for missing columns and adds them if needed.
    """
    from sqlalchemy import inspect, text
    from datetime import datetime
    
    inspector = inspect(engine)
    
    # Check users table
    if 'users' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('users')]
        if 'is_verified' not in columns:
            logger.info("Adding missing 'is_verified' column to users table")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 0"))
                conn.commit()
            logger.info("Successfully added 'is_verified' column")
        
        if 'profile_data' not in columns:
            logger.info("Adding missing 'profile_data' column to users table")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN profile_data TEXT"))
                conn.commit()
            logger.info("Successfully added 'profile_data' column")
    
    # Check messages table
    if 'messages' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('messages')]
        if 'is_transcript' not in columns:
            logger.info("Adding missing 'is_transcript' column to messages table")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE messages ADD COLUMN is_transcript BOOLEAN DEFAULT 0"))
                conn.commit()
            logger.info("Successfully added 'is_transcript' column")
        
        if 'updated_at' not in columns:
            logger.info("Adding missing 'updated_at' column to messages table")
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE messages ADD COLUMN updated_at TIMESTAMP DEFAULT '{datetime.utcnow().isoformat()}'"))
                conn.commit()
            logger.info("Successfully added 'updated_at' column to messages")
    
    # Check conversations table
    if 'conversations' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('conversations')]
        if 'updated_at' not in columns:
            logger.info("Adding missing 'updated_at' column to conversations table")
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE conversations ADD COLUMN updated_at TIMESTAMP DEFAULT '{datetime.utcnow().isoformat()}'"))
                conn.commit()
            logger.info("Successfully added 'updated_at' column to conversations")
    
    # Check important_memories table
    if 'important_memories' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('important_memories')]
        
        if 'conversation_id' not in columns:
            logger.info("Adding missing 'conversation_id' column to important_memories table")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE important_memories ADD COLUMN conversation_id INTEGER"))
                conn.commit()
            logger.info("Successfully added 'conversation_id' column to important_memories")
        
        if 'updated_at' not in columns:
            logger.info("Adding missing 'updated_at' column to important_memories table")
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE important_memories ADD COLUMN updated_at TIMESTAMP DEFAULT '{datetime.utcnow().isoformat()}'"))
                conn.commit()
            logger.info("Successfully added 'updated_at' column to important_memories")
    
    # Check assessments table
    if 'assessments' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('assessments')]
        if 'updated_at' not in columns:
            logger.info("Adding missing 'updated_at' column to assessments table")
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE assessments ADD COLUMN updated_at TIMESTAMP DEFAULT '{datetime.utcnow().isoformat()}'"))
                conn.commit()
            logger.info("Successfully added 'updated_at' column to assessments")


def apply_migrations() -> None:
    """Apply all pending migrations using our migration system."""
    try:
        # Only import here to avoid circular imports
        from src.mental_health_coach.utils.migrations import apply_migrations as run_migrations
        
        if DATABASE_URL.startswith("sqlite"):
            # Extract file path from SQLite URL
            db_path = DATABASE_URL.replace("sqlite:///", "")
            if db_path.startswith("./"):
                db_path = db_path[2:]
                
            logger.info(f"Applying migrations to {db_path}")
            run_migrations(db_path)
        else:
            logger.warning("Migration system currently only supports SQLite databases")
    except ImportError:
        logger.warning("Migration system not available")
    except Exception as e:
        logger.error(f"Error applying migrations: {e}")
        # Don't raise the exception - we want the app to start even if migrations fail
        # The check_and_update_schema function will handle critical schema issues


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
    
    # Apply any pending migrations
    apply_migrations()
    
    # Check and update schema as a fallback
    check_and_update_schema() 