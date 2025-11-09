# Document Builder Platform

The Document Builder platform produces professional-grade Word and PowerPoint outputs by orchestrating three Python services and a user agent. Architecture, APIs, algorithms, and data contracts are defined in the design documents under `ApplicationDesign/` and must be followed precisely.

## Repository Layout

- `ApplicationDesign/` – Authoritative design specifications for components and interfaces
- `services/` – Source code for the Content Intake Service, Gestalt Design Engine, Document Formatter Service, and User Agent orchestrator (to be implemented)
- `tests/` – Pytest-based automated tests (to be implemented)
- `config/` – Shared configuration artifacts (schemas, OpenAPI specs, etc.)
- `scripts/` – Developer tooling, automation scripts, and maintenance utilities
- `ApplicationTaskList/` – Active engineering task lists referencing design documents
- `Archive/` – Historical design iterations for reference only

## Getting Started

1. **Review the design**: Read the relevant document in `ApplicationDesign/` before writing any code.
2. **Set up environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```
3. **Configuration**: Populate `.env` based on `.env.example`. Do not commit actual secrets.
4. **Development workflow**:
   - Implement components within `services/` following their design documents.
   - Add tests under `tests/` with structure mirroring service modules.
   - Update `ApplicationTaskList/` when tasks are created or completed.

## Documentation

- Global architecture: `ApplicationDesign/ApplicationDesign.MD`
- Component designs: `ApplicationDesign/ContentIntakeServiceDesign.MD`, `ApplicationDesign/GestaltDesignEngineDesign.MD`, `ApplicationDesign/DocumentFormatterServiceDesign.MD`, `ApplicationDesign/UserAgentWorkflowDesign.MD`
- Interface contracts: `ApplicationDesign/ContentIntentInterfaceDesign.MD`, `ApplicationDesign/LayoutSpecificationInterfaceDesign.MD`

## Contribution Principles

- Follow `.cursor/rules/project-rules.md` and `Claude.MD` for shared development guidelines.
- No new technology, dependencies, or architectural deviations without explicit approval.
- Ensure tests cover critical functionality and reside in the `tests/` folder.
- Maintain configuration in `.env`; never hardcode secrets or environment-specific values.

