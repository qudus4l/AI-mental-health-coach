# Database Guide

This document provides guidance on working with the database in the Mental Health Coach application.

## Database Overview

The application uses SQLite for development and can be configured to use PostgreSQL in production. The database contains tables for users, conversations, messages, and other entities needed for the application's functionality.

## Schema Management

### Adding New Models

When creating a new model:

1. Define the model in an appropriate file in `src/mental_health_coach/models/`
2. Import the model in `src/mental_health_coach/database.py` within the `init_db()` function
3. Create a schema file in `src/mental_health_coach/schemas/` for API interactions
4. Add a migration for the new model (see below)

### Modifying Existing Models

When modifying an existing model:

1. Update the model in the appropriate file
2. Update the corresponding schema if needed
3. **Important**: Create a migration for the schema change

### Adding New Fields to Existing Models

When adding a new field to an existing model:

1. Add the field to the model
2. Add the field to the corresponding schema if needed
3. Create a migration for the schema change

## Migration System

The application uses a simple migration system to manage database schema changes.

### Creating a New Migration

To create a new migration:

```bash
python -m src.mental_health_coach.utils.migrations create migration_name "Description of what this migration does"
```

This creates a new migration file in the migrations directory. Edit this file to implement your migration.

After implementing the migration, add it to the `MIGRATIONS` list in `src/mental_health_coach/utils/migrations.py`.

### Running Migrations

To apply all pending migrations:

```bash
python -m src.mental_health_coach.utils.migrations apply path/to/database.db
```

The application also automatically runs migrations during startup.

## SQLite Limitations

SQLite has several limitations with schema changes:

- Cannot drop columns
- Cannot rename columns
- Cannot change column types
- Limited support for foreign key constraints

For these operations, you may need to:

1. Create a new table with the desired schema
2. Copy data from the old table to the new table
3. Drop the old table
4. Rename the new table to the original name

## Troubleshooting

### "No such column" Error

If you see a "no such column" error, it means the database schema doesn't match the model definition. This can happen if:

1. You added a column to a model but didn't create a migration
2. A migration failed to apply properly

To fix this:

1. Check if the column exists in the database:
   ```bash
   sqlite3 mental_health_coach.db "PRAGMA table_info(table_name);"
   ```
2. Run migrations:
   ```bash
   python -m src.mental_health_coach.utils.migrations apply mental_health_coach.db
   ```
3. If the issue persists, you may need to manually add the column:
   ```bash
   sqlite3 mental_health_coach.db "ALTER TABLE table_name ADD COLUMN column_name COLUMN_TYPE;"
   ```

### "Table already exists" Error

This error occurs when trying to create a table that already exists. To fix this:

1. Check if you're running database initialization multiple times
2. Make sure your migration doesn't try to create an existing table

## Best Practices

1. **Always use migrations** for schema changes
2. Test migrations on a development database before applying to production
3. Back up the database before applying migrations
4. Keep migrations small and focused on a single change
5. Never modify existing migrations that have been applied to production databases
6. Create a new migration instead of changing an existing one
7. Always include both `up` and `down` methods in migrations
8. Use meaningful names for migrations
9. Document what each migration does
10. Version control your migrations
11. Test your code with the migrated schema 