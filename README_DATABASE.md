# Database Setup for Content Intake Service

This document explains how to set up and manage the PostgreSQL database for the Content Intake Service.

## Prerequisites

- PostgreSQL 15+ running in a container or locally
- Python 3.11+
- Dependencies installed (`pip install -r requirements.txt`)

## Quick Start with Docker

### 1. Start PostgreSQL Container

```bash
docker run --name document-builder-postgres \
  -e POSTGRES_DB=document_builder \
  -e POSTGRES_USER=docbuilder \
  -e POSTGRES_PASSWORD=changeme \
  -p 5432:5432 \
  -d postgres:15-alpine
```

### 2. Verify PostgreSQL is Running

```bash
docker ps | grep document-builder-postgres
```

### 3. Run Database Migrations

```bash
# From the project root
cd /path/to/Document-Builder/worktrees/content-intake

# Run migrations
python scripts/init_db.py

# Or use Alembic directly
alembic upgrade head
```

## Database Schema

The database includes the following tables:

### sessions
- Stores intake session metadata
- Fields: session_id, status, design_intent, constraints, proposal_id, etc.
- Status enum: draft, normalizing, ready, layout_queued, layout_processing, layout_complete, failed

### content_blocks
- Stores individual content blocks for each session
- Fields: block_id, session_id, type, level, sequence, text, language, detected_role, metrics
- Foreign key to sessions table

### image_assets
- Stores image metadata for each session
- Fields: image_id, session_id, uri, format, width_px, height_px, alt_text, content_role
- Foreign key to sessions table

### idempotency_keys
- Stores idempotency keys for request deduplication
- Fields: idempotency_key, session_id, created_at, expires_at

## Managing Migrations

### Create a New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create an empty migration
alembic revision -m "Description of changes"
```

### Run Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade <revision>

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision>
```

### Check Current Version

```bash
alembic current
```

### View Migration History

```bash
alembic history
```

## Environment Variables

Configure database connection via environment variables:

```bash
export DATABASE_URL="postgresql://docbuilder:changeme@localhost:5432/document_builder"
```

Or use `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
# Edit .env with your database credentials
```

## Database Connection Pooling

The service uses SQLAlchemy connection pooling:

- **Pool size**: 10 connections
- **Max overflow**: 20 connections
- **Pre-ping**: Enabled (tests connection before use)

Configuration in `services/content_intake/database/connection.py`.

## Troubleshooting

### Connection Refused

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check PostgreSQL logs
docker logs document-builder-postgres

# Verify port is accessible
telnet localhost 5432
```

### Migration Errors

```bash
# Reset database (WARNING: destroys all data)
docker exec -it document-builder-postgres psql -U docbuilder -d document_builder -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Re-run migrations
alembic upgrade head
```

### Permission Errors

Ensure the database user has necessary permissions:

```sql
GRANT ALL PRIVILEGES ON DATABASE document_builder TO docbuilder;
GRANT ALL ON SCHEMA public TO docbuilder;
```

## Production Considerations

- Use connection pooling (already configured)
- Enable SSL/TLS for database connections
- Use strong passwords (not 'changeme')
- Regular backups with point-in-time recovery
- Monitor connection pool usage
- Set up read replicas for scaling
- Use managed PostgreSQL services (RDS, Cloud SQL, etc.)

## Testing

To run tests against the database:

```bash
# Run with test database
export DATABASE_URL="postgresql://docbuilder:changeme@localhost:5432/document_builder_test"
pytest tests/
```
