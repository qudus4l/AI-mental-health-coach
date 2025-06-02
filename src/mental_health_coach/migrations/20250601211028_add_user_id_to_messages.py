"""Migration: add_user_id_to_messages

Add user_id column to messages table
"""

def up(conn):
    """Apply the migration.
    
    Args:
        conn: SQLite connection object.
    """
    conn.execute("ALTER TABLE messages ADD COLUMN user_id INTEGER REFERENCES users(id)")


def down(conn):
    """Roll back the migration.
    
    Args:
        conn: SQLite connection object.
    """
    # SQLite doesn't support dropping columns without recreating the table
    # This would require a more complex migration to remove a column
    pass
