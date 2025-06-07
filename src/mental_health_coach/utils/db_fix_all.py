"""Comprehensive database schema fix script.

This script checks and fixes all database schema issues in one go.
"""

import logging
from sqlalchemy import create_engine, inspect, text
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///mental_health_coach.db")
engine = create_engine(DATABASE_URL)


def fix_all_schema_issues():
    """Fix all known database schema issues."""
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # 1. Fix users table
        if 'users' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'is_verified' not in columns:
                logger.info("Adding is_verified column to users table")
                conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 0"))
                conn.commit()
            
            if 'profile_data' not in columns:
                logger.info("Adding profile_data column to users table")
                conn.execute(text("ALTER TABLE users ADD COLUMN profile_data TEXT"))
                conn.commit()
        
        # 2. Fix messages table
        if 'messages' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('messages')]
            
            if 'is_transcript' not in columns:
                logger.info("Adding is_transcript column to messages table")
                conn.execute(text("ALTER TABLE messages ADD COLUMN is_transcript BOOLEAN DEFAULT 0"))
                conn.commit()
            
            if 'updated_at' not in columns:
                logger.info("Adding updated_at column to messages table")
                conn.execute(text(f"ALTER TABLE messages ADD COLUMN updated_at TIMESTAMP DEFAULT '{datetime.utcnow().isoformat()}'"))
                conn.commit()
        
        # 3. Fix conversations table
        if 'conversations' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('conversations')]
            
            if 'updated_at' not in columns:
                logger.info("Adding updated_at column to conversations table")
                conn.execute(text(f"ALTER TABLE conversations ADD COLUMN updated_at TIMESTAMP DEFAULT '{datetime.utcnow().isoformat()}'"))
                conn.commit()
        
        # 4. Fix important_memories table
        if 'important_memories' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('important_memories')]
            
            if 'updated_at' not in columns:
                logger.info("Adding updated_at column to important_memories table")
                conn.execute(text(f"ALTER TABLE important_memories ADD COLUMN updated_at TIMESTAMP DEFAULT '{datetime.utcnow().isoformat()}'"))
                conn.commit()
        
        # 5. Fix homework_assignments table
        if 'homework_assignments' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('homework_assignments')]
            
            if 'updated_at' not in columns:
                logger.info("Adding updated_at column to homework_assignments table")
                conn.execute(text(f"ALTER TABLE homework_assignments ADD COLUMN updated_at TIMESTAMP DEFAULT '{datetime.utcnow().isoformat()}'"))
                conn.commit()
        
        # 6. Fix assessments table
        if 'assessments' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('assessments')]
            
            if 'updated_at' not in columns:
                logger.info("Adding updated_at column to assessments table")
                conn.execute(text(f"ALTER TABLE assessments ADD COLUMN updated_at TIMESTAMP DEFAULT '{datetime.utcnow().isoformat()}'"))
                conn.commit()
        
        # 7. Fix user_profiles table
        if 'user_profiles' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('user_profiles')]
            
            if 'updated_at' not in columns:
                logger.info("Adding updated_at column to user_profiles table")
                conn.execute(text(f"ALTER TABLE user_profiles ADD COLUMN updated_at TIMESTAMP DEFAULT '{datetime.utcnow().isoformat()}'"))
                conn.commit()
        
        # 8. Fix session_schedules table
        if 'session_schedules' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('session_schedules')]
            
            if 'updated_at' not in columns:
                logger.info("Adding updated_at column to session_schedules table")
                conn.execute(text(f"ALTER TABLE session_schedules ADD COLUMN updated_at TIMESTAMP DEFAULT '{datetime.utcnow().isoformat()}'"))
                conn.commit()
        
        # 9. Fix emergency_contacts table
        if 'emergency_contacts' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('emergency_contacts')]
            
            if 'updated_at' not in columns:
                logger.info("Adding updated_at column to emergency_contacts table")
                conn.execute(text(f"ALTER TABLE emergency_contacts ADD COLUMN updated_at TIMESTAMP DEFAULT '{datetime.utcnow().isoformat()}'"))
                conn.commit()
        
        logger.info("All schema fixes applied successfully!")


def create_test_user():
    """Create a test user for testing purposes."""
    from src.mental_health_coach.auth.security import get_password_hash
    
    with engine.connect() as conn:
        # Check if test user already exists
        result = conn.execute(text("SELECT id FROM users WHERE email = 'test@example.com'"))
        if result.fetchone():
            logger.info("Test user already exists")
            return
        
        # Create test user
        hashed_password = get_password_hash("testpassword123")
        conn.execute(text("""
            INSERT INTO users (email, hashed_password, first_name, last_name, is_active, is_verified, created_at)
            VALUES (:email, :password, :first_name, :last_name, 1, 1, :created_at)
        """), {
            "email": "test@example.com",
            "password": hashed_password,
            "first_name": "Test",
            "last_name": "User",
            "created_at": datetime.utcnow().isoformat()
        })
        conn.commit()
        logger.info("Test user created: test@example.com / testpassword123")


if __name__ == "__main__":
    logger.info("Starting comprehensive database fix...")
    fix_all_schema_issues()
    create_test_user()
    logger.info("Database fix complete!") 