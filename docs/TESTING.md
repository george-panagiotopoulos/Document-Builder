# Testing Guide

## Services Status

All services are running and healthy:
- **Content Intake Service**: http://localhost:8001
- **Gestalt Design Engine**: http://localhost:8002
- **Document Formatter Service**: http://localhost:8003

## Quick Health Checks

```bash
# Check all services are healthy
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

Expected response: `{"status":"healthy","service":"<service-name>"}`

## Testing Methods

### 1. Interactive API Documentation (Swagger UI)

The easiest way to test the APIs is through the interactive Swagger UI:

- **Content Intake API**: http://localhost:8001/docs
- **Gestalt Engine API**: http://localhost:8002/docs
- **Document Formatter API**: http://localhost:8003/docs

You can:
- Browse all available endpoints
- See request/response schemas
- Test endpoints directly from the browser
- View example requests

### 2. Web UI (Content Intake Service)

Access the web interface at: **http://localhost:8001/**

Features:
- Create new sessions
- View session dashboard
- Submit sessions for processing
- View session details

### 3. Command Line Testing (cURL)

#### Test 1: Create a Session

```bash
curl -X POST "http://localhost:8001/v1/intake/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "content_blocks": [
      {
        "block_id": "block-001",
        "type": "heading",
        "level": 1,
        "sequence": 0,
        "text": "Quarterly Business Review - Q4 2024",
        "language": "en"
      },
      {
        "block_id": "block-002",
        "type": "paragraph",
        "level": 0,
        "sequence": 1,
        "text": "Our team achieved remarkable growth this quarter with revenue increasing by 45% year-over-year.",
        "language": "en"
      }
    ],
    "images": [],
    "design_intent": {
      "purpose": "presentation",
      "audience": "executive",
      "tone": "formal",
      "goals": ["clarity", "impact"]
    },
    "constraints": {
      "visual_density": "balanced",
      "max_pages": 10
    }
  }'
```

**Expected Response:**
```json
{
  "session_id": "sess-...",
  "status": "DRAFT",
  "created_at": "2025-11-09T...",
  "proposal_id": null
}
```

Save the `session_id` from the response for next steps.

#### Test 2: Get Session Details

```bash
# Replace SESSION_ID with the session_id from Test 1
curl "http://localhost:8001/v1/intake/sessions/SESSION_ID"
```

#### Test 3: Submit Session for Layout Generation

```bash
# Replace SESSION_ID with your session_id
curl -X POST "http://localhost:8001/v1/intake/sessions/SESSION_ID/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "layout_mode": "rule_only"
  }'
```

**Expected Response:**
```json
{
  "session_id": "sess-...",
  "status": "LAYOUT_PENDING",
  "created_at": "2025-11-09T...",
  "proposal_id": "prop-..."
}
```

#### Test 4: Check Layout Generation Status

```bash
# Replace SESSION_ID with your session_id
curl -X POST "http://localhost:8001/v1/intake/sessions/SESSION_ID/check-status"
```

Poll this endpoint until `status` becomes `"LAYOUT_COMPLETE"`.

#### Test 5: Get Layout Specification

```bash
# Replace PROPOSAL_ID with the proposal_id from Test 3
curl "http://localhost:8002/v1/layout/proposals/PROPOSAL_ID/spec"
```

#### Test 6: Generate PowerPoint Document

```bash
# First, get the layout spec (from Test 5), then:
curl -X POST "http://localhost:8003/v1/render/presentations" \
  -H "Content-Type: application/json" \
  -d '{
    "layout_specification": {
      "schema_version": "1.1",
      "proposal_id": "prop-...",
      "document_type": "presentation",
      "structure": [...]
    }
  }'
```

#### Test 7: Generate Word Document

```bash
curl -X POST "http://localhost:8003/v1/render/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "layout_specification": {
      "schema_version": "1.1",
      "proposal_id": "prop-...",
      "document_type": "word",
      "structure": [...]
    }
  }'
```

### 4. Automated Tests

Run the full test suite:

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run only unit tests
python3 -m pytest tests/unit/ -v

# Run only integration tests
python3 -m pytest tests/integration/ -v

# Run specific test file
python3 -m pytest tests/unit/test_gestalt_principles.py -v

# Run with coverage report
python3 -m pytest tests/ --cov=services --cov-report=html
# Coverage report will be in infrastructure/test-reports/htmlcov/index.html
```

### 5. End-to-End Workflow Test

The integration test `tests/integration/test_e2e_workflow.py` tests the complete workflow:

```bash
python3 -m pytest tests/integration/test_e2e_workflow.py::test_end_to_end_workflow -v -s
```

This test:
1. Creates a session
2. Submits it for layout generation
3. Polls for completion
4. Retrieves the layout specification
5. Generates PowerPoint and Word documents
6. Verifies files were created

## Viewing Logs

Monitor service logs in real-time:

```bash
# View all logs
tail -f infrastructure/logs/*.log

# View specific service log
tail -f infrastructure/logs/Content\ Intake\ Service.log
tail -f infrastructure/logs/Gestalt\ Design\ Engine.log
tail -f infrastructure/logs/Document\ Formatter.log
```

## Common Issues

### Database Connection Errors
- Ensure PostgreSQL container is running: `docker ps | grep postgres`
- Check database is accessible: `pg_isready -h localhost -p 5432`
- Verify `.env` has correct `DATABASE_URL`

### Service Not Responding
- Check if service is running: `ps aux | grep uvicorn`
- Check logs for errors: `tail -f infrastructure/logs/*.log`
- Restart services: `./stop.sh && ./start.sh`

### Test Failures
- Ensure all services are running
- Check database migrations are applied: `python3 scripts/init_db.py`
- Verify `.env` file exists and is properly configured

## Next Steps

1. **Explore the APIs**: Visit http://localhost:8001/docs to see all available endpoints
2. **Try the UI**: Go to http://localhost:8001/ to create sessions via the web interface
3. **Run tests**: Execute `python3 -m pytest tests/ -v` to verify everything works
4. **Check logs**: Monitor `infrastructure/logs/*.log` to see what's happening

