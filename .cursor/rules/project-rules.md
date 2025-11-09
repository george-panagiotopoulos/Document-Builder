# IMPORTANT: Any changes to this file must be reflected in Claude.MD to remain in sync (except this first line which references Claude.MD)

# Document Builder Project Rules

## Component Overview

### Component A: Content Intake Service
- **Purpose**: Validates payloads, normalizes text and images, persists session context, and invokes downstream layout generation
- **Tech Stack**: Python (Flask/FastAPI), PostgreSQL, Object Storage (S3-compatible), JWT authentication
- **Design Document**: `/ApplicationDesign/ContentIntakeServiceDesign.MD`

### Component B: Gestalt Design Engine
- **Purpose**: Applies rule-based and AI-assisted design principles to synthesize layout specifications for documents and slides
- **Tech Stack**: Python (Flask/FastAPI), PostgreSQL (JSONB), OpenAI/Anthropic APIs, NumPy for calculations
- **Design Document**: `/ApplicationDesign/GestaltDesignEngineDesign.MD`

### Component C: Document Formatter Service
- **Purpose**: Converts layout specifications into Office-compatible outputs using python-pptx and python-docx
- **Tech Stack**: Python (Flask/FastAPI), python-docx, python-pptx, Pillow (PIL), Object Storage (S3-compatible)
- **Design Document**: `/ApplicationDesign/DocumentFormatterServiceDesign.MD`

### User Agent
- **Purpose**: Orchestrates the end-to-end workflow by invoking REST APIs across all three services
- **Tech Stack**: Python (CLI/web app), REST client libraries
- **Design Document**: `/ApplicationDesign/UserAgentWorkflowDesign.MD`

## Design Documentation Requirements

1. **Always follow the design documents**: Before implementing any feature, carefully read the relevant design document in `/ApplicationDesign/`. The design documents are the source of truth for architecture, APIs, data structures, and algorithms.

2. **No deviations without approval**: If you need to deviate from the design documents, ask the user first. Document any approved deviations.

3. **Reference design documents in code**: Include comments referencing specific sections of design documents when implementing complex logic (e.g., "Implements Gestalt Proximity Principle - see GestaltDesignEngineDesign.MD section 6.1").

## Technology Stack Management

1. **No new tech without approval**: Do not introduce new libraries, frameworks, or technologies without explicit user confirmation. Stick to the tech stack defined in the design documents.

2. **Python ecosystem only**: All components use Python. Use standard libraries when possible, then well-established packages (python-docx, python-pptx, Flask/FastAPI, PostgreSQL drivers).

3. **Environment configuration**: All configuration must come from `.env` file (see coding principles below).

## Coding Principles

1. **Testing**: Always write comprehensive tests for key functionality. All tests go in `/test` folder. Tests should be in Python using pytest. Aim for >80% code coverage on critical paths.

2. **No stubbed data without confirmation**: Never stub or mock data unless explicitly confirmed by the user. If stubbing is necessary, place all stubbed data in separate files starting with `stub_` prefix (e.g., `stub_test_content.json`) so code can react appropriately.

3. **Configuration management**: No hardcoded values. Everything must be configurable via `.env` file. Use a single `.env` file for the entire project. Document all environment variables in `.env.example`.

4. **When in doubt, ask**: If you're uncertain about implementation approach, design decisions, or requirements, always ask the user rather than making assumptions.

5. **Error handling**: Implement comprehensive error handling with meaningful error messages. Log errors with appropriate context (correlation IDs, stack traces for debugging).

6. **Code organization**: Follow Python best practices - use modules, packages, and clear separation of concerns. Each component should be independently deployable.

7. **API design**: Follow RESTful principles and OpenAPI 3.0 specifications. Version all APIs (`/v1/...`). Include proper HTTP status codes and error responses.

8. **Security**: Always validate inputs, sanitize data before AI calls, use parameterized queries for database operations, and follow JWT authentication patterns defined in design documents.

9. **Documentation**: Write clear docstrings for all functions and classes. Include parameter descriptions, return values, and any exceptions that may be raised.

10. **Performance**: Be mindful of performance targets defined in design documents. Use async processing for long-running operations. Implement caching where appropriate (as specified in design docs).

