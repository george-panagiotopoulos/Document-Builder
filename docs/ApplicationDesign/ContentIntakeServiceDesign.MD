# Content Intake Service Design

## 1. Purpose
The Content Intake Service (Component A) receives source material, intent metadata, and assets from the user agent. It validates and normalizes the submission, assembles a Content-Intent Package (CIP), and coordinates downstream calls to the Gestalt Design Engine. The service enforces submission policies, manages session state, and exposes REST endpoints for workflow automation.

## 2. Responsibilities
- Accept text blocks, images, and design intent descriptors through an authenticated REST API.
- Normalize and classify content (e.g., detect headings, lists, tables) without altering the author’s tone.
- Validate image formats, dimensions, and accessibility metadata.
- Persist intake sessions, raw content, and derived descriptors.
- Trigger layout proposal generation and track lifecycle states (e.g., `submitted`, `analyzing`, `layout_ready`).
- Provide status and retrieval endpoints for the user agent.
- Enforce security guardrails (quota, rate limits, payload size caps).

## 3. External Interfaces

### 3.1 REST API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/intake/sessions` | Create an intake session, upload content payload, return `session_id`. |
| `GET` | `/v1/intake/sessions/{session_id}` | Retrieve session metadata, processing state, and downstream artifact references. |
| `POST` | `/v1/intake/sessions/{session_id}/submit` | Finalize content, trigger layout generation in the Gestalt Design Engine. |
| `GET` | `/v1/intake/sessions/{session_id}/artifacts` | List generated layout specifications and final document artifact IDs. |
| `DELETE` | `/v1/intake/sessions/{session_id}` | Cancel and purge a session that has not been rendered. |

All endpoints require JWT bearer tokens with scopes: `intake.create`, `intake.read`, or `intake.manage`.

### 3.2 Downstream Calls
- `POST /v1/layout/proposals` on the Gestalt Design Engine to request layout generation.
- `POST /v1/render/documents` and `/v1/render/presentations` on the Document Formatter Service once layout specifications are accepted.

## 4. Data Model
- **Session**: `session_id`, `created_at`, `created_by`, `status`, `preferred_outputs`, `constraint_profile`.
- **ContentBlock**: `block_id`, `session_id`, `type`, `sequence`, `text_payload`, `source_language`, `detected_role` (heading, paragraph, list item, quote).
- **ImageAsset**: `image_id`, `session_id`, `storage_uri`, `alt_text`, `width_px`, `height_px`, `dominant_colors`.
- **IntentDescriptor**: `session_id`, `purpose`, `audience`, `goals[]`, `constraints{}`, `brand_profile_ref`.

Relational storage (PostgreSQL) maintains normalized tables with foreign keys. Binary assets are stored in object storage using pre-signed upload URLs.

## 5. Processing Workflow
1. **Session Creation**: Validate payload size (<25 MB), register session state `draft`.
2. **Content Normalization**: Tokenize text, detect structural cues (Markdown headings, numbering), enrich metadata such as estimated reading time.
3. **Asset Validation**: Reject unsupported formats, downscale images that exceed max dimensions (4096x4096) while preserving aspect ratio.
4. **Constraint Consolidation**: Merge design goals with default style guides; store canonical constraint profile.
5. **Layout Request Dispatch**: On submission, bundle normalized data into the CIP schema and call the Gestalt Design Engine. Capture response ID and transition session state accordingly.
6. **Artifact Tracking**: Monitor asynchronous jobs using callbacks or polling endpoints; update session with layout specification pointers and rendered artifact IDs.

## 6. Error Handling
- **Validation errors**: Return `422 Unprocessable Entity` with detailed field-level messages.
- **Quota breaches**: Return `429 Too Many Requests`; log audit events.
- **Downstream failures**: Retry with exponential backoff for transient errors; escalate to `502 Bad Gateway` if the Gestalt Design Engine remains unavailable.
- **Data persistence issues**: Use transaction rollbacks; surface `500 Internal Server Error` with correlation IDs for observability.

## 7. Security and Compliance
- JWT validation with issuer pinning, audience checks, and scope enforcement.
- Payload scanning for restricted content; configurable blocklists.
- Encryption at rest for session metadata (PostgreSQL TDE or application-layer encryption for sensitive fields).
- Audit logging for session creation, update, and deletion events with immutable storage retention.

## 8. Performance and Scalability
- Stateless application instances behind a load balancer; leverage autoscaling based on CPU and queue depth.
- Streaming uploads via multipart to avoid loading entire files into memory.
- Async worker pool for expensive normalization tasks (e.g., language detection) to keep API latency below 400 ms P95.

## 9. Observability
- Structured logging (JSON) with correlation IDs propagated to downstream services.
- Metrics: request latency, validation failure counts, session state transitions, downstream call success rates.
- Tracing: OpenTelemetry spans for each workflow stage, including external API calls and database interactions.

## 10. Dependencies
- PostgreSQL for session and metadata persistence.
- Object storage (S3-compatible) for binary assets.
- Message queue (e.g., Amazon SQS or Kafka) for job tracking when formatting tasks are asynchronous.
- Authentication provider issuing JWTs (e.g., Auth0, custom IdP).

## 11. Failure Modes and Mitigation
- **Downstream outage**: Pause new submissions, notify user agent via status field `layout_unavailable`.
- **Storage outage**: Cache payloads locally with retry policies, enforce back-pressure to prevent data loss.
- **Schema evolution**: Version CIP schema, enforce backward compatibility through migration layer.

## 12. Open Questions
- Should the service support partial updates to sessions (PATCH) for large content sets?
- Which SLA targets must be met before auto-scaling kicks in (hysteresis values)?
- Do we require geo-replication for intake data in multi-region deployments?

