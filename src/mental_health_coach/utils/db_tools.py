"""Database utility tools for maintenance operations.

This module provides command-line utilities for database maintenance operations
such as creating, checking, and updating the database schema.
"""

import argparse
import logging
import sys
import os

# Ensure the parent directory is in the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.mental_health_coach.database import init_db, check_and_update_schema, engine
from src.mental_health_coach.models.base import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_all_tables():
    """Create all tables defined in the models."""
    try:
        logger.info("Creating all database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully created all tables.")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        sys.exit(1)


def check_schema():
    """Check if the database schema matches the models."""
    try:
        logger.info("Checking database schema...")
        check_and_update_schema()
        logger.info("Schema check completed successfully.")
    except Exception as e:
        logger.error(f"Schema check failed: {e}")
        sys.exit(1)


def reset_database():
    """Drop all tables and recreate them (WARNING: This will delete all data)."""
    try:
        confirm = input("This will delete ALL data in the database. Type 'yes' to confirm: ")
        if confirm.lower() != "yes":
            logger.info("Database reset cancelled.")
            return
        
        logger.warning("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("Successfully dropped all tables.")
        
        logger.info("Recreating all tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully recreated all tables.")
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        sys.exit(1)


def main():
    """Main entry point for the database tools."""
    parser = argparse.ArgumentParser(description="Database maintenance tools")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # create_tables command
    subparsers.add_parser("create_tables", help="Create all database tables")
    
    # check_schema command
    subparsers.add_parser("check_schema", help="Check if the database schema matches the models")
    
    # reset_database command
    subparsers.add_parser("reset_database", help="Reset the database (WARNING: This will delete all data)")
    
    # init_db command (runs both create_tables and check_schema)
    subparsers.add_parser("init_db", help="Initialize the database (create tables and check schema)")
    
    args = parser.parse_args()
    
    if args.command == "create_tables":
        create_all_tables()
    elif args.command == "check_schema":
        check_schema()
    elif args.command == "reset_database":
        reset_database()
    elif args.command == "init_db":
        init_db()
        logger.info("Database initialization completed successfully.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 