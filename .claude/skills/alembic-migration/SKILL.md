---
name: alembic-migration
description: Generate, review, and run Alembic database migrations
triggers:
  - /alembic
  - alembic migration
  - run migration
---

# Alembic Migration Skill

## Overview
This skill guides Claude through generating, reviewing, and running Alembic migrations safely for a FastAPI + SQLAlchemy + PostgreSQL project.

## Project Context
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Migration tool:** Alembic
- **Database:** PostgreSQL
- **Models location:** `app/models/`
- **Migrations location:** `alembic/versions/`
- **Working directory:** project root (where `alembic.ini` lives)

---

## Critical Rules
These rules override all other instructions in this skill.

- NEVER run `alembic upgrade head` without first showing the user the generated migration file and receiving explicit approval
- NEVER run more than one migration at a time without permission from the user
- NEVER run `alembic downgrade` in any form without explicit permission from the user
- NEVER delete or modify files in `alembic/versions/` without explicit permission
- ALWAYS show the full migration file contents to the user before running it
- ALWAYS confirm the migration ran successfully before ending the task
- If anything looks unexpected in the generated migration, STOP and ask the user before proceeding


## Step 1: Identify the change
Before generating a migration, identify:
- Which model file was changed (`app/models/*.py`)
- What type of change was made:
  - New table → new model class
  - New column → new `Column()` on existing model
  - Renamed column → changed column name in model
  - Deleted column → removed `Column()` from model
  - New constraint → added `UniqueConstraint`, `Index`, etc.

---

## Step 2: Generate the migration
Run autogenerate with a descriptive message:
```bash
alembic revision --autogenerate -m "<description of change>"
```

Good message examples:
- `"add photo_url to user_plants"`
- `"rename watering_interval_days to default_watering_interval_days"`
- `"add unique constraint to user_plant"`

Bad message examples:
- `"schema update"`
- `"changes"`
- `"fix"`

---

## Step 3: Review the generated file
Always open and review the file in `alembic/versions/` before running it.

### Check for these common autogenerate mistakes:

#### Column renames
Autogenerate does NOT detect renames — it generates a drop + add instead, which loses data.

If you see this:
```python
op.drop_column('table', 'old_name')
op.add_column('table', sa.Column('new_name', ...))
```

Replace with:
```python
op.alter_column('table', 'old_name', new_column_name='new_name')
```

#### Enum changes
Autogenerate sometimes misses Postgres enum type changes. Verify enum columns are correct.

#### JSON columns
Autogenerate may not correctly diff JSON column contents. Verify any JSON-related changes manually.

#### Missing changes
If autogenerate produces an empty migration when you expected changes:
- Check that all models are imported in `alembic/env.py`
- Check that `target_metadata = Base.metadata` is set in `alembic/env.py`
- Verify the model changes were saved

### Verify the downgrade function
Every migration should have a working `downgrade()` that reverses the `upgrade()` exactly.

For `alter_column` renames, downgrade should reverse the rename:
```python
def downgrade():
    op.alter_column('table', 'new_name', new_column_name='old_name')
```

For new columns, downgrade should drop them:
```python
def downgrade():
    op.drop_column('table', 'column_name')
```

---

## Step 4: Run the migration
Once reviewed:
```bash
alembic upgrade head
```

Verify it ran:
```bash
alembic current
```

You should see the new revision ID with `(head)` next to it.

---

## Step 5: Verify in the database
Connect to psql and verify the change:
```bash
# Check columns on a table
\d table_name

# Check current migration version
SELECT * FROM alembic_version;
```

Or check in pgAdmin by refreshing the table in the sidebar.

---

## Rollback procedure
If something went wrong:
```bash
alembic downgrade -1   # roll back one migration
```

---

## Common errors and fixes

| Error | Cause | Fix |
|---|---|---|
| `Target database is not up to date` | Unapplied migrations exist | Run `alembic upgrade head` first |
| `Can't locate revision` | Migration file deleted or moved | Check `alembic/versions/` |
| `Column already exists` | Migration ran twice | Check `alembic current` |
| `relation does not exist` | Table missing, migration not run | Run `alembic upgrade head` |
| Empty autogenerate | Models not imported in `env.py` | Add imports to `alembic/env.py` |

---

## Checklist before every migration
- [ ] Model change is saved
- [ ] Migration generated with descriptive message
- [ ] Generated file reviewed for drop+add instead of rename
- [ ] `downgrade()` function is correct
- [ ] `alembic upgrade head` ran successfully
- [ ] Change verified in pgAdmin or psql