"""Database module for the mental health coach application.

This module provides the database session and base model class.
"""

import os
import logging
from typing import Generator
import sqlite3

from sqlalchemy import create_engine, inspect, MetaData, Table, Column, Boolean, Text
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
    """Check for schema differences and update the database schema.
    
    This function checks if the database schema matches the SQLAlchemy models
    and adds missing columns if needed. This helps avoid errors when models
    are updated but the database schema hasn't been migrated.
    """
    inspector = inspect(engine)
    
    # Check User table for is_verified column
    if "users" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("users")]
        
        # Check for is_verified column
        if "is_verified" not in columns:
            logger.info("Adding missing column 'is_verified' to users table")
            try:
                # For SQLite, we need to use raw SQL for adding columns
                if DATABASE_URL.startswith("sqlite"):
                    conn = engine.connect()
                    conn.execute("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 0 NOT NULL")
                    conn.commit()
                    conn.close()
                else:
                    # For other databases, we can use SQLAlchemy's more abstract approach
                    meta = MetaData()
                    meta.reflect(bind=engine)
                    users_table = Table('users', meta)
                    
                    column = Column('is_verified', Boolean, default=False, nullable=False)
                    column_name = column.compile(dialect=engine.dialect)
                    column_type = column.type.compile(engine.dialect)
                    
                    engine.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_type} DEFAULT False NOT NULL')
                
                logger.info("Successfully added 'is_verified' column to users table")
            except Exception as e:
                logger.error(f"Failed to add column: {e}")
                raise
        
        # Check for profile_data column
        if "profile_data" not in columns:
            logger.info("Adding missing column 'profile_data' to users table")
            try:
                # For SQLite, we need to use raw SQL for adding columns
                if DATABASE_URL.startswith("sqlite"):
                    conn = engine.connect()
                    conn.execute("ALTER TABLE users ADD COLUMN profile_data TEXT")
                    conn.commit()
                    conn.close()
                else:
                    # For other databases, we can use SQLAlchemy's more abstract approach
                    meta = MetaData()
                    meta.reflect(bind=engine)
                    users_table = Table('users', meta)
                    
                    column = Column('profile_data', Text, nullable=True)
                    column_name = column.compile(dialect=engine.dialect)
                    column_type = column.type.compile(engine.dialect)
                    
                    engine.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_type}')
                
                logger.info("Successfully added 'profile_data' column to users table")
            except Exception as e:
                logger.error(f"Failed to add column: {e}")
                raise


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