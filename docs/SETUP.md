# Document Builder - Setup Guide

This guide will help you set up the Document Builder platform for local development.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 14 or higher (or Docker for containerized database)
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Document-Builder
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred editor
nano .env  # or vim, code, etc.
```

**Important environment variables to configure:**

- `DATABASE_URL` - PostgreSQL connection string
- `CONTENT_INTAKE_PORT` - Port for Content Intake Service (default: 8001)
- `GESTALT_ENGINE_PORT` - Port for Gestalt Engine (default: 8002)
- `DOCUMENT_FORMATTER_PORT` - Port for Document Formatter (default: 8003)
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` - Database credentials
- `SECRET_KEY` - Change to a random secret key for production

See `.env.example` for all available configuration options and their defaults.

### 4. Set Up PostgreSQL Database

#### Option A: Using Docker (Recommended for Development)

```bash
# Start PostgreSQL container
docker run --name docbuilder-postgres \
  -e POSTGRES_USER=docbuilder \
  -e POSTGRES_PASSWORD=changeme \
  -e POSTGRES_DB=document_builder \
  -p 5432:5432 \
  -d postgres:14
```

#### Option B: Using Local PostgreSQL Installation

```bash
# Create database and user
sudo -u postgres psql
CREATE USER docbuilder WITH PASSWORD 'changeme';
CREATE DATABASE document_builder OWNER docbuilder;
GRANT ALL PRIVILEGES ON DATABASE document_builder TO docbuilder;
\q
```

### 5. Run Database Migrations

```bash
# Run Alembic migrations (from project root)
alembic -c infrastructure/alembic.ini upgrade head
```

### 6. Start the Services

You can start services individually or use Docker Compose for the full stack.

#### Option A: Start Individual Services

**Content Intake Service:**
```bash
cd services/content_intake
uvicorn services.content_intake.main:app --reload --port ${CONTENT_INTAKE_PORT:-8001}
```

**Gestalt Design Engine:**
```bash
cd services/gestalt_engine
uvicorn services.gestalt_engine.main:app --reload --port ${GESTALT_ENGINE_PORT:-8002}
```

**Document Formatter Service:**
```bash
cd services/document_formatter
uvicorn services.document_formatter.main:app --reload --port ${DOCUMENT_FORMATTER_PORT:-8003}
```

#### Option B: Start All Services with Docker Compose

```bash
docker-compose -f infrastructure/docker/docker-compose.yml up
```

### 7. Verify Installation

Open your browser and check the following endpoints:

- Content Intake Service: http://localhost:8001/health
- Content Intake UI: http://localhost:8001/
- API Documentation: http://localhost:8001/docs
- Gestalt Engine: http://localhost:8002/health
- Document Formatter: http://localhost:8003/health

## Development Workflow

### Using Git Worktrees

This project uses Git worktrees for parallel development across feature branches:

```bash
# List all worktrees
git worktree list

# Work on a specific feature
cd worktrees/content-intake

# Make changes, commit, and push
git add .
git commit -m "Your commit message"
git push origin feature/content-intake
```

See the main README.md for more details on the Git worktree workflow.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=services --cov-report=html

# Run specific service tests
pytest tests/content_intake/
```

### Database Management

```bash
# Create a new migration (from project root)
alembic -c infrastructure/alembic.ini revision --autogenerate -m "Description of changes"

# Apply migrations
alembic -c infrastructure/alembic.ini upgrade head

# Rollback last migration
alembic -c infrastructure/alembic.ini downgrade -1

# View migration history
alembic -c infrastructure/alembic.ini history
```

## Configuration Details

### Environment Files

- `.env.example` - Template with all configuration options and documentation
- `.env` - Your local configuration (not tracked in git)
- `.env.test` - Test environment configuration (optional)

### Service Ports

Default ports for local development:

| Service | Port | Environment Variable |
|---------|------|---------------------|
| Content Intake | 8001 | CONTENT_INTAKE_PORT |
| Gestalt Engine | 8002 | GESTALT_ENGINE_PORT |
| Document Formatter | 8003 | DOCUMENT_FORMATTER_PORT |
| PostgreSQL | 5432 | POSTGRES_PORT |
| Redis | 6379 | REDIS_PORT |

### Database Connection

The `DATABASE_URL` follows the format:
```
postgresql://username:password@host:port/database_name
```

Example:
```
DATABASE_URL=postgresql://docbuilder:changeme@localhost:5432/document_builder
```

For testing, you can use a separate database:
```
TEST_DATABASE_URL=postgresql://docbuilder:changeme@localhost:5432/document_builder_test
```

## Troubleshooting

### Database Connection Issues

**Error: "could not connect to server"**
- Verify PostgreSQL is running: `pg_isready`
- Check connection string in `.env`
- Ensure PostgreSQL is listening on the correct port

**Error: "password authentication failed"**
- Verify username and password in `.env`
- Check `pg_hba.conf` authentication settings

### Port Already in Use

If you see "Address already in use":
```bash
# Find process using port 8001
lsof -i :8001

# Kill the process
kill -9 <PID>

# Or use a different port in .env
CONTENT_INTAKE_PORT=8011
```

### Migration Issues

**Error: "Target database is not up to date"**
```bash
# Check current migration status
alembic -c infrastructure/alembic.ini current

# Apply pending migrations
alembic -c infrastructure/alembic.ini upgrade head
```

**Error: "Can't locate revision"**
```bash
# Reset migration history (development only!)
alembic -c infrastructure/alembic.ini downgrade base
alembic -c infrastructure/alembic.ini upgrade head
```

### Module Import Errors

Ensure you're running from the correct directory and virtual environment is activated:
```bash
# Activate virtual environment
source .venv/bin/activate

# Run from project root
cd /path/to/Document-Builder
uvicorn services.content_intake.main:app --reload
```

## Production Deployment

For production deployment:

1. **Update .env for production:**
   - Set `ENVIRONMENT=production`
   - Set `DEBUG=false`
   - Use strong passwords and secret keys
   - Configure proper CORS origins
   - Enable HTTPS

2. **Use production-grade database:**
   - Use managed PostgreSQL (RDS, Cloud SQL, etc.)
   - Configure connection pooling
   - Set up backups

3. **Run with production server:**
   ```bash
   # Use gunicorn with uvicorn workers
   gunicorn services.content_intake.main:app \
     -w 4 \
     -k uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8001
   ```

4. **Set up reverse proxy (nginx):**
   - Configure SSL/TLS
   - Set up load balancing
   - Configure rate limiting

5. **Monitor services:**
   - Enable Prometheus metrics
   - Set up logging aggregation
   - Configure health checks

See `infrastructure/docker/docker-compose.yml` and `infrastructure/k8s/` directory for container orchestration examples.

## Next Steps

- Read the architecture overview in `ApplicationDesign/ApplicationDesign.MD` (in this docs directory)
- Review service-specific design documents in `ApplicationDesign/` (in this docs directory)
- Explore the API documentation at http://localhost:8001/docs
- Try creating a session via the UI at http://localhost:8001/

## Getting Help

- Check existing documentation in `ApplicationDesign/` (in this docs directory)
- Review service-specific README files (README_UI.md, README_DATABASE.md in this docs directory)
- Check the troubleshooting section above
- Review application logs for detailed error messages
