# Document Builder Platform

The Document Builder platform produces professional-grade Word and PowerPoint outputs by orchestrating three Python services and a user agent. Architecture, APIs, algorithms, and data contracts are defined in the design documents under `docs/ApplicationDesign/` and must be followed precisely.

## Repository Layout

- `docs/ApplicationDesign/` – Authoritative design specifications for components and interfaces
- `services/` – Source code for the Content Intake Service, Gestalt Design Engine, Document Formatter Service, and User Agent orchestrator (to be implemented)
- `tests/` – Pytest-based automated tests (to be implemented)
- `config/` – Shared configuration artifacts (schemas, OpenAPI specs, etc.)
- `scripts/` – Developer tooling, automation scripts, and maintenance utilities
- `infrastructure/` – Infrastructure configuration (alembic, docker, k8s, logs, test reports, dev tools)
- `docs/ApplicationTaskList/` – Active engineering task lists referencing design documents
- `Archive/` – Historical design iterations for reference only
- `worktrees/` – Git worktrees for parallel development (local only, not tracked in git)

**Note:** Some configuration files (`.pre-commit-config.yaml`, `.python-version`, `pyproject.toml`) appear as symlinks in the root directory. These are required by tools (pre-commit, pyenv, pytest) that expect config files in the project root. The actual files are stored in `infrastructure/` and `infrastructure/dev-tools/`.

## Getting Started

**For detailed setup instructions, see [docs/SETUP.md](docs/SETUP.md).**

Quick start:

1. **Review the design**: Read the relevant document in `docs/ApplicationDesign/` before writing any code.
2. **Set up environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your configuration
   # IMPORTANT: .env is REQUIRED in production/staging environments
   # Default values are only for development and will cause errors in production
   ```
3. **Set up database**:
   ```bash
   # Start PostgreSQL (Docker)
   docker run --name docbuilder-postgres \
     -e POSTGRES_USER=docbuilder \
     -e POSTGRES_PASSWORD=changeme \
     -e POSTGRES_DB=document_builder \
     -p 5432:5432 -d postgres:14

   # Run migrations
   alembic -c infrastructure/alembic.ini upgrade head
   ```
4. **Start services**:
   ```bash
   # Content Intake Service
   uvicorn services.content_intake.main:app --reload --port 8001
   ```
5. **Development workflow**:
   - This project uses **Git worktrees** for parallel development. See "Git Worktree Workflow" section below.
   - Implement components within `services/` following their design documents.
   - Add tests under `tests/` with structure mirroring service modules.
   - Update `docs/ApplicationTaskList/` when tasks are created or completed.

## Documentation

- Global architecture: `docs/ApplicationDesign/ApplicationDesign.MD`
- Component designs: `docs/ApplicationDesign/ContentIntakeServiceDesign.MD`, `docs/ApplicationDesign/GestaltDesignEngineDesign.MD`, `docs/ApplicationDesign/DocumentFormatterServiceDesign.MD`, `docs/ApplicationDesign/UserAgentWorkflowDesign.MD`
- Interface contracts: `docs/ApplicationDesign/ContentIntentInterfaceDesign.MD`, `docs/ApplicationDesign/LayoutSpecificationInterfaceDesign.MD`

## Git Worktree Workflow

This project uses Git worktrees to enable parallel development. Each feature branch has its own working directory under `worktrees/`.

### Quick Start

```bash
# List all worktrees
git worktree list

# Work in a specific component
cd worktrees/content-intake
# You're now on feature/content-intake branch - work normally

# Merge back to main (from main repo directory)
cd /path/to/Document-Builder
git checkout main
git merge feature/content-intake
git push origin main
```

### Available Worktrees

- `worktrees/tooling` → `feature/tooling`
- `worktrees/content-intake` → `feature/content-intake`
- `worktrees/gestalt-engine` → `feature/gestalt-engine`
- `worktrees/document-formatter` → `feature/document-formatter`
- `worktrees/user-agent` → `feature/user-agent`
- `worktrees/testing` → `feature/testing`
- `worktrees/operations` → `feature/operations`

For detailed workflow instructions, see `.cursor/rules/project-rules.md` or `Claude.MD` (Git Worktree Workflow section).

## Contribution Principles

- Follow `.cursor/rules/project-rules.md` and `Claude.MD` for shared development guidelines.
- No new technology, dependencies, or architectural deviations without explicit approval.
- Ensure tests cover critical functionality and reside in the `tests/` folder.
- Maintain configuration in `.env`; never hardcode secrets or environment-specific values.
- Use Git worktrees for parallel development - see workflow section above.

