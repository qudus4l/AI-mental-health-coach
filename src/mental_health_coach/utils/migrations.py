"""Migration system for database schema changes.

This module provides a basic migration system for tracking and applying
database schema changes. It is designed to be simple yet effective for
smaller projects without the complexity of Alembic.
"""

import os
import json
import logging
import sqlite3
import datetime
from typing import List, Dict, Any, Callable

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Path to store migration information
MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "../migrations")
MIGRATION_RECORD_FILE = os.path.join(MIGRATIONS_DIR, "applied_migrations.json")

# Ensure migrations directory exists
os.makedirs(MIGRATIONS_DIR, exist_ok=True)


class Migration:
    """Represents a database migration.
    
    Attributes:
        name: Unique name of the migration
        description: Description of what the migration does
        up: Function to apply the migration
        down: Function to roll back the migration
    """
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        up: Callable[[sqlite3.Connection], None], 
        down: Callable[[sqlite3.Connection], None]
    ):
        """Initialize a new migration.
        
        Args:
            name: Unique name of the migration
            description: Description of what the migration does
            up: Function to apply the migration
            down: Function to roll back the migration
        """
        self.name = name
        self.description = description
        self.up = up
        self.down = down


# List of all migrations
MIGRATIONS: List[Migration] = [
    Migration(
        name="add_is_verified_to_users",
        description="Add is_verified column to users table",
        up=lambda conn: conn.execute("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 0 NOT NULL"),
        down=lambda conn: logger.warning("SQLite does not support dropping columns")
    ),
    Migration(
        name="add_profile_data_to_users",
        description="Add profile_data column to users table",
        up=lambda conn: conn.execute("ALTER TABLE users ADD COLUMN profile_data TEXT"),
        down=lambda conn: logger.warning("SQLite does not support dropping columns")
    ),
    Migration(
        name="add_summary_to_conversations",
        description="Add summary column to conversations table",
        up=lambda conn: conn.execute("ALTER TABLE conversations ADD COLUMN summary TEXT"),
        down=lambda conn: logger.warning("SQLite does not support dropping columns")
    ),
    Migration(
        name="add_user_id_to_messages",
        description="Add user_id column to messages table",
        up=lambda conn: conn.execute("ALTER TABLE messages ADD COLUMN user_id INTEGER REFERENCES users(id)"),
        down=lambda conn: logger.warning("SQLite does not support dropping columns")
    ),
    # Add more migrations here as needed
]


def get_applied_migrations() -> List[str]:
    """Get the list of applied migrations.
    
    Returns:
        List of names of applied migrations.
    """
    if not os.path.exists(MIGRATION_RECORD_FILE):
        return []
    
    try:
        with open(MIGRATION_RECORD_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def record_migration(name: str) -> None:
    """Record that a migration has been applied.
    
    Args:
        name: Name of the migration that was applied.
    """
    applied = get_applied_migrations()
    if name not in applied:
        applied.append(name)
    
    with open(MIGRATION_RECORD_FILE, "w") as f:
        json.dump(applied, f)


def apply_migrations(db_path: str) -> None:
    """Apply all unapplied migrations.
    
    Args:
        db_path: Path to the SQLite database file.
    """
    # Get list of applied migrations
    applied = get_applied_migrations()
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    
    try:
        # Apply each unapplied migration
        for migration in MIGRATIONS:
            if migration.name not in applied:
                logger.info(f"Applying migration: {migration.name} - {migration.description}")
                try:
                    migration.up(conn)
                    conn.commit()
                    record_migration(migration.name)
                    logger.info(f"Successfully applied migration: {migration.name}")
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Failed to apply migration {migration.name}: {e}")
                    raise
    finally:
        conn.close()


def create_migration(name: str, description: str) -> None:
    """Create a new migration template file.
    
    Args:
        name: Name of the migration.
        description: Description of what the migration does.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{name}.py"
    filepath = os.path.join(MIGRATIONS_DIR, filename)
    
    template = f'''"""Migration: {name}

{description}
"""

def up(conn):
    """Apply the migration.
    
    Args:
        conn: SQLite connection object.
    """
    # Implement the migration here
    # Example:
    # conn.execute("ALTER TABLE users ADD COLUMN new_column TEXT")
    pass


def down(conn):
    """Roll back the migration.
    
    Args:
        conn: SQLite connection object.
    """
    # Implement the rollback here
    # Example:
    # conn.execute("ALTER TABLE users DROP COLUMN new_column")
    # Note: SQLite has limited support for schema changes
    pass
'''
    
    with open(filepath, "w") as f:
        f.write(template)
    
    logger.info(f"Created migration template: {filepath}")
    logger.info("Edit this file to implement your migration, then add it to the MIGRATIONS list in migrations.py")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m src.mental_health_coach.utils.migrations apply <db_path>")
        print("  python -m src.mental_health_coach.utils.migrations create <name> <description>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "apply":
        if len(sys.argv) < 3:
            print("Missing database path")
            print("Usage: python -m src.mental_health_coach.utils.migrations apply <db_path>")
            sys.exit(1)
        
        db_path = sys.argv[2]
        apply_migrations(db_path)
    
    elif command == "create":
        if len(sys.argv) < 4:
            print("Missing migration name or description")
            print("Usage: python -m src.mental_health_coach.utils.migrations create <name> <description>")
            sys.exit(1)
        
        name = sys.argv[2]
        description = sys.argv[3]
        create_migration(name, description)
    
    else:
        print(f"Unknown command: {command}")
        print("Usage:")
        print("  python -m src.mental_health_coach.utils.migrations apply <db_path>")
        print("  python -m src.mental_health_coach.utils.migrations create <name> <description>")
        sys.exit(1) 