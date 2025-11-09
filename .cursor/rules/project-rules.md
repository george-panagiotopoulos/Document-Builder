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

## Git Worktree Workflow

This project uses Git worktrees to enable parallel development across multiple components. Each feature branch has its own working directory under `worktrees/`.

### Available Worktrees

- `worktrees/tooling` → `feature/tooling` (Repository setup, schemas, tooling)
- `worktrees/content-intake` → `feature/content-intake` (Component A)
- `worktrees/gestalt-engine` → `feature/gestalt-engine` (Component B)
- `worktrees/document-formatter` → `feature/document-formatter` (Component C)
- `worktrees/user-agent` → `feature/user-agent` (Orchestrator)
- `worktrees/testing` → `feature/testing` (Shared testing infrastructure)
- `worktrees/operations` → `feature/operations` (Deployment & operations)

### Working in a Worktree

1. **Navigate to worktree directory**:
   ```bash
   cd worktrees/content-intake
   # You're now on feature/content-intake branch
   ```

2. **Normal git operations**: Work, commit, push as usual - all operations are isolated to that branch.

3. **Switching contexts**: No need to stash or commit - just `cd` to another worktree directory.

### Merging Worktrees Back to Main

**Recommended merge order** (based on dependencies):
1. `feature/tooling` (foundation)
2. `feature/content-intake` (Component A)
3. `feature/gestalt-engine` (Component B - depends on A)
4. `feature/document-formatter` (Component C - depends on B)
5. `feature/user-agent` (depends on A, B, C)
6. `feature/testing` (can merge incrementally)
7. `feature/operations` (deployment - merge last)

**Merge process**:
```bash
# 1. Complete work in worktree
cd worktrees/content-intake
git add .
git commit -m "Complete feature implementation"
git push origin feature/content-intake

# 2. Switch to main and update
cd /path/to/Document-Builder  # Main repo directory
git checkout main
git pull origin main

# 3. Merge feature branch
git merge feature/content-intake

# 4. Test merged code, then push
git push origin main

# 5. Update dependent worktrees
cd worktrees/gestalt-engine
git fetch origin
git merge origin/main  # Get latest merged changes

# 6. Clean up (optional - after merge is complete)
cd /path/to/Document-Builder
git branch -d feature/content-intake
git push origin --delete feature/content-intake
git worktree remove worktrees/content-intake
```

### Best Practices

1. **Keep feature branches synced**: Regularly merge `origin/main` into your feature branch to avoid large conflicts.
2. **One branch per worktree**: Each branch can only be checked out in one worktree at a time.
3. **Worktrees share repository**: Commits, branches, and remotes are shared across all worktrees.
4. **Use Pull Requests**: For collaboration, create PRs on GitHub before merging to main.
5. **List worktrees**: Use `git worktree list` to see all active worktrees and their branches.

