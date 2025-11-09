# Content-Intent Interface Design

## 1. Purpose
The Content-Intent Interface defines the contract between the Content Intake Service and the Gestalt Design Engine. It packages normalized source material, imagery, and design intent into a JSON payload referred to as the Content-Intent Package (CIP). The contract ensures both services share a consistent understanding of content semantics, constraints, and processing expectations.

## 2. Producers and Consumers
- **Producer**: Content Intake Service (`POST /v1/layout/proposals`).
- **Consumer**: Gestalt Design Engine (validates, processes, and acknowledges the CIP).
- **Optional Consumer**: Future analytics services that may replay CIPs for experimentation.

## 3. Transport and Protocol
- REST over HTTPS, `application/json` content type.
- Endpoint: `POST https://design-engine.internal/v1/layout/proposals`.
- Authentication: JWT bearer token with scope `layout.generate`.
- Idempotency supported via `Idempotency-Key` header (UUID).

## 4. Payload Overview
```json
{
  "schema_version": "1.1",
  "session_id": "sess-12345",
  "submission_id": "subm-2025-11-09T08:45:00Z",
  "content": {
    "blocks": [],
    "images": []
  },
  "design_intent": {},
  "constraints": {},
  "metadata": {}
}
```

### 4.1 Content Blocks
Each block captures text elements in document order.
- `block_id` (string, required): Stable identifier.
- `type` (enum): `heading`, `paragraph`, `list`, `quote`, `table`, `callout`.
- `level` (integer): Heading level or list depth; defaults to `0`.
- `sequence` (integer): Ordering token.
- `text` (string): UTF-8 content; Markdown and HTML stripped except explicit formatting markers.
- `language` (ISO 639-1 code): Auto-detected or client-provided.
- `detected_role` (enum): `introduction`, `analysis`, `summary`, `action`, etc.
- `metrics`: Derived attributes (estimated reading time, word count).

### 4.2 Image Assets
- `image_id` (string, required).
- `uri` (string): Secure object storage reference.
- `format` (enum): `png`, `jpg`, `svg`.
- `width_px`, `height_px` (integer).
- `alt_text` (string, required for accessibility).
- `content_role` (enum): `illustration`, `data`, `process`, `hero`.
- `dominant_palette`: Optional array of hex colors.

### 4.3 Design Intent
- `purpose` (enum): `report`, `presentation`, `proposal`, `playbook`.
- `audience` (enum): `executive`, `technical`, `customer`, `internal`.
- `tone` (enum): `formal`, `conversational`, `persuasive`, `educational`.
- `goals` (array): e.g., `["clarity", "impact", "brevity"]`.
- `primary_actions` (array): Intended reader actions (e.g., `["approve_budget"]`).
- `success_metrics` (array): How success is measured (e.g., `["time_to_understand_minutes<=5"]`).

### 4.4 Constraints
- `visual_density` (enum): `tight`, `balanced`, `airy`.
- `color_policy` (object): `primary`, `secondary`, contrast requirements.
- `brand_guidelines` (object reference): Link to stored brand pack.
- `document_preferences`: Word-specific options (e.g., columns, headings).
- `presentation_preferences`: Slide count targets, animation allowance, slide aspect ratio.

### 4.5 Metadata
- `initiated_by`: User or automation identifier.
- `submitted_at`: ISO timestamp.
- `source_system`: Client identifier (e.g., `web_app`, `cli`).
- `trace_id`: Correlation ID for distributed tracing.

## 5. Validation Rules
- `schema_version` must be supported by the Gestalt Design Engine; requests with unsupported versions return `426 Upgrade Required`.
- `content.blocks` length ≤ 1,000; `content.images` length ≤ 200.
- Required fields: `session_id`, `submission_id`, at least one content block.
- `text` size per block ≤ 10,000 characters.
- `alt_text` mandatory except when `content_role = "hero"` and `decorative=true`.
- `color_policy.primary` must be valid HEX color; contrast ratios ≥ 4.5:1 when paired with background.
- JSON schema validation executed by both producer and consumer to avoid contract drift.

## 6. Response Structure
Successful submission returns `202 Accepted` with body:
```json
{
  "proposal_id": "lsp-78901",
  "status": "queued",
  "estimated_completion_seconds": 4
}
```
Failure responses include structured error codes, e.g., `400` with `code="CIP_SCHEMA_MISMATCH"` and list of offending paths.

## 7. Versioning Strategy
- Semantic versioning (`major.minor`).
- Backward-compatible additions allowed on minor increments.
- Major version changes require new endpoint path (`/v2/layout/proposals`) and coexistence period.
- Producer includes `Accept-Version` header to negotiate optional features.

## 8. Observability
- Producer and consumer log `submission_id`, `proposal_id`, `session_id`, and `trace_id`.
- Metrics: CIP size distribution, validation failure count, average time between CIP submission and layout completion.
- Emit CloudEvents `content.submitted` and `layout.requested` for audit streams (Kafka optional).

## 9. Security Considerations
- Payload encrypted in transit (TLS 1.2+).
- Sensitive fields (e.g., proprietary text) redacted from logs by both parties.
- Idempotency key prevents accidental duplicate submissions.
- Rate limiting: max 30 CIP submissions per minute per client.

## 10. Error Handling
- **Client errors**: 4xx with descriptive codes (`CIP_VALIDATION_ERROR`, `CIP_SIZE_LIMIT_EXCEEDED`, etc.).
- **Server errors**: 5xx with correlation ID; retries recommended with backoff.
- **Partial acceptance**: Not permitted; entire payload must pass validation.

## 11. Future Enhancements
- Allow references to structured data sources (e.g., CSV URIs) for chart generation.
- Embed heuristic scores from intake (readability index, sentiment).
- Support multilingual packages with translation hints for cross-locale output.

