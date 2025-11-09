# Document Formatter Service Design

## 1. Purpose
The Document Formatter Service (Component C) transforms Layout Specification Packages (LSP) into Microsoft Word and PowerPoint artifacts. It leverages python-docx and python-pptx libraries, ensuring outputs align with prescribed coordinates, styling, and hierarchy decisions made by the Gestalt Design Engine.

## 2. Responsibilities
- Receive layout specifications and render `.docx` and `.pptx` files with deterministic fidelity.
- Enforce formatter capability constraints (templates, text handling, image processing).
- Manage asynchronous rendering jobs when processing time exceeds synchronous thresholds.
- Store generated artifacts and expose retrieval endpoints to the user agent.
- Provide validation feedback when requested layouts cannot be satisfied exactly.

## 3. API Surface
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/render/documents` | Accept an LSP and initiate Word document generation; returns `render_job_id`. |
| `POST` | `/v1/render/presentations` | Accept an LSP and initiate PowerPoint generation; returns `render_job_id`. |
| `GET` | `/v1/render/jobs/{render_job_id}` | Retrieve job status (`queued`, `processing`, `complete`, `failed`) and artifact references. |
| `GET` | `/v1/artifacts/{artifact_id}` | Download generated files or obtain time-limited access URLs. |
| `POST` | `/v1/render/jobs/{render_job_id}/cancel` | Attempt to cancel in-progress rendering. |

Authentication scopes: `render.create`, `render.read`, `render.manage`.

## 4. Rendering Pipeline
1. **Request Validation**: Confirm LSP schema version, verify signatures of upstream services, and ensure requested output formats are supported.
2. **Preparation**: Resolve referenced assets (images, brand themes) from object storage. Convert units to formatter-specific metrics (EMU for pptx, twips for docx).
3. **Engine Selection**: Route to the Word renderer or PowerPoint renderer depending on `document_type`.
4. **Layout Execution**: Create slides/pages, add content per element definitions (text, images, tables, shapes), and apply styling tokens.
5. **Post-Processing**: Run validation checks (contrast ratios, text overflow). When issues are detected, apply correction heuristics or annotate warnings.
6. **Artifact Storage**: Persist output files to object storage with metadata (checksum, size, generation time).
7. **Response**: Return status and artifact references; notify upstream service via callback or rely on polling.

## 5. Word Renderer Design
- Implements flow-aware assembly: sorts elements by `position.y`, applies Word style mapping, and uses text boxes for absolute positioning when required.
- Applies custom paragraph and character formatting aligned with Gestalt hierarchy tags (e.g., `Heading 1`, `Heading 2`, `Body`).
- Handles tables by mapping column definitions to python-docx table structures and auto-sizing columns within margins.
- Embeds images as inline or floating objects depending on layout plan; enforces target width and height with optional cropping.

## 6. PowerPoint Renderer Design
- Configures slide dimensions (16:9 default) and selects `slide_layout` mappings per template.
- Adds shapes, text boxes, tables, and images at precise coordinates, converting inches to EMU values.
- Supports multi-column text by splitting boxes or leveraging layout placeholders.
- Applies theme colors and fonts by referencing or constructing slide masters.
- Records fallback adjustments (e.g., text shrink-to-fit when overflow occurs) in the job report.

## 7. Validation and Compliance
- **Pre-flight validator**: Checks element bounds, template availability, color formatting, and image format compatibility before rendering.
- **Post-render validator**: Ensures resulting file opens successfully in Microsoft Office and includes expected slide/page counts.
- **Accessibility checks**: Optional pass verifying alt text presence, heading order, and color contrast thresholds.

## 8. Storage Strategy
- Generated artifacts stored in object storage with structured keys: `artifacts/{session_id}/{render_job_id}/{filename}`.
- Metadata stored in PostgreSQL with fields: `artifact_id`, `session_id`, `proposal_id`, `file_type`, `checksum`, `expires_at`.
- Support retention policies and deletion requests via background tasks.

## 9. Scalability and Performance
- Worker-based architecture using a job queue (e.g., Celery + Redis, AWS SQS, or Kafka consumers).
- Vertical scaling limited by CPU and memory requirements of python-docx/pptx; horizontal scaling achieved by adding workers.
- Target render times: <3 seconds for standard reports (20 pages), <2 seconds for standard decks (12 slides).
- Utilize caching of compiled templates (e.g., slide masters) to avoid repeated initialization overhead.

## 10. Observability
- Emit job lifecycle events (`job_received`, `render_started`, `render_complete`, `render_failed`).
- Metrics: render latency, failure rates by cause, average file size, retry counts.
- Store rendering warnings for consumption by the user agent (e.g., `text_shrunk=true`, `image_scaled=true`).

## 11. Security Controls
- Verify upstream service signatures to prevent unauthorized rendering requests.
- Enforce artifact access through signed URLs; default expiry 24 hours.
- Sanitize file names and metadata to prevent injection or path traversal attacks.
- Regularly update python-docx and python-pptx to incorporate security patches.

## 12. Failure Scenarios
- **Malformed LSP**: Reject with `400 Bad Request`, log schema mismatch.
- **Asset retrieval failure**: Retry with exponential backoff; mark job failed if assets remain unreachable.
- **Rendering exception**: Capture stack trace, store in job report, and mark status `failed`.
- **Storage outage**: Queue completed artifacts locally and retry uploads; expose status `pending_storage`.

## 13. Future Enhancements
- Support progressive streaming for large files (>200 MB).
- Introduce PDF export via additional rendering backend (e.g., weasyprint or LibreOffice headless).
- Implement diff-based re-rendering to avoid full regeneration when minor layout adjustments occur.

