# Database

The application uses SQLAlchemy as the ORM and supports SQLite (development) and PostgreSQL (production).

## Schema

The database consists of the following main tables:

- `users` – User accounts and authentication.
- `recipes` – Recipe master data.
- `recipe_categories` – Categories for recipes (e.g., Breakfast, Dessert).
- `ingredients` – Ingredient definitions.
- `recipe_ingredients` – Many‑to‑many relationship between recipes and ingredients.
- `recipe_steps` – Step‑by‑step instructions for a recipe.
- `recipe_images` – Images attached to recipes.
- `ratings` – User ratings (1‑5 stars) for recipes.
- `comments` – User comments on recipes.
- `favorites` – Bookmarked recipes by users.
- `images` – Central image storage.
- `logs` – Audit log for all create/update/delete operations.

## Migrations

The project uses **Alembic** for database migrations. The migration scripts are located in the `alembic/` directory.

### Creating a New Migration

After modifying a SQLAlchemy model, generate a migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Review the generated migration script in `alembic/versions/` and adjust if needed.

### Applying Migrations

To upgrade the database to the latest version:

```bash
alembic upgrade head
```

To downgrade one revision:

```bash
alembic downgrade -1
```

## Seeding

Initial data (admin user, default categories, etc.) is loaded by `utils/init_db.py`. This script is intended for development and first‑time setup.

### Running the Seeder

```bash
python -m utils.init_db
```

The script will:

1. Create the database tables (if they don't exist).
2. Insert the admin user (login: `admin`, password: `admin`).
3. Insert default recipe categories.
4. Insert default ingredient categories.
5. Insert sample ingredients.

**Warning**: The seeder is idempotent but will reset certain data in development. Do not run it on a production database.

## Production Database

For production, set the `DATABASE_URL` environment variable to a PostgreSQL connection string, e.g.:

```
DATABASE_URL=postgresql://user:password@localhost/recipe_db
```

The application will automatically use the appropriate dialect.

## Backup and Restore

### SQLite

Backup:
```bash
sqlite3 recipe.db ".backup backup.db"
```

Restore:
```bash
sqlite3 recipe.db ".restore backup.db"
```

### PostgreSQL

Backup:
```bash
pg_dump recipe_db > backup.sql
```

Restore:
```bash
psql recipe_db < backup.sql
```

## Indexes

The following indexes are defined to improve query performance:

- `idx_recipe_status` – Filtering by status.
- `idx_recipe_category_id` – Joins with categories.
- `idx_recipe_author_id` – Filtering by author.
- `idx_recipe_title_normalized` – Search by normalized title.
- Indexes on foreign keys (automatically created by SQLAlchemy in some cases).

## Audit Logging

The `logs` table records every create, update, and delete operation. Each log entry includes:

- `table_name`: The affected table.
- `record_id`: The primary key of the affected row.
- `operation`: `created`, `updated`, or `deleted`.
- `user_id`: Who performed the operation.
- `timestamp`: When the operation occurred.
- `old_values` / `new_values`: JSON snapshots of the change (for updates).

Logging is handled automatically by the `Log` class from the Bafser framework.