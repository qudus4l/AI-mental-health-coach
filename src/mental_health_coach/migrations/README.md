# Database Migrations

This directory contains database migration scripts for managing schema changes in the Mental Health Coach application.

## Why Migrations?

As the application evolves, the database schema needs to change to accommodate new features or fix issues. Migrations provide a way to:

1. Track schema changes over time
2. Apply changes consistently across different environments
3. Roll back changes if needed
4. Keep the database in sync with the application models

## How to Use Migrations

### Running Migrations

To apply all pending migrations:

```bash
python -m src.mental_health_coach.utils.migrations apply path/to/database.db
```

### Creating a New Migration

To create a new migration:

```bash
python -m src.mental_health_coach.utils.migrations create migration_name "Description of what this migration does"
```

This creates a new migration file in the migrations directory. Edit this file to implement your migration.

After implementing the migration, add it to the `MIGRATIONS` list in `src/mental_health_coach/utils/migrations.py`.

### Best Practices

1. **Never modify existing migrations** that have been applied to production databases.
2. Create a new migration instead of changing an existing one.
3. Always test migrations on a development database before applying to production.
4. Make sure each migration has proper up and down methods.
5. Keep migrations small and focused on a single change.

## Automatic Migration Check

The application automatically checks for and applies pending migrations during startup. This is handled by the `check_and_update_schema()` function in the database module.

## Migration Structure

Each migration should include:

1. A unique name
2. A description of what it does
3. An `up` function to apply the migration
4. A `down` function to roll back the migration (when possible)

Example:

```python
Migration(
    name="add_is_verified_to_users",
    description="Add is_verified column to users table",
    up=lambda conn: conn.execute("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 0 NOT NULL"),
    down=lambda conn: logger.warning("SQLite does not support dropping columns")
)
```

## Limitations

SQLite has limited support for schema changes. In particular:

- You cannot drop columns
- You cannot rename columns
- You cannot change column types

For these operations, you may need to create a new table, copy data, and drop the old table. 