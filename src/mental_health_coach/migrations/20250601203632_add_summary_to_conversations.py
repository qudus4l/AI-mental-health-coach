"""Migration: add_summary_to_conversations

Add summary column to conversations table
"""

def up(conn):
    """Apply the migration.
    
    Args:
        conn: SQLite connection object.
    """
    conn.execute("ALTER TABLE conversations ADD COLUMN summary TEXT")


def down(conn):
    """Roll back the migration.
    
    Args:
        conn: SQLite connection object.
    """
    # SQLite doesn't support dropping columns without recreating the table
    # This would require a more complex migration to remove a column
    pass
