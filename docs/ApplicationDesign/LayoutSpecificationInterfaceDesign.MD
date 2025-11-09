# Layout Specification Interface Design

## 1. Purpose
The Layout Specification Interface governs how the Gestalt Design Engine delivers layout plans to the Document Formatter Service. The Layout Specification Package (LSP) encapsulates all instructions needed to generate Word and PowerPoint artifacts, including structural hierarchy, positioning, styling, and rationale metadata.

## 2. Producers and Consumers
- **Producer**: Gestalt Design Engine (`GET /v1/layout/proposals/{proposal_id}/spec`).
- **Consumer**: Document Formatter Service (`POST /v1/render/documents`, `/v1/render/presentations`).
- **Secondary Consumers**: QA tooling, analytics, or downstream renderers (e.g., PDF) that rely on the same specification.

## 3. Transport and Protocol
- REST over HTTPS with `application/json` payloads.
- When the formatter retrieves an LSP, it provides the `proposal_id` or receives the LSP in the POST body.
- Authentication: JWT with scope `render.create`.
- Payload size limit: 5 MB per LSP.

## 4. Package Structure
```json
{
  "schema_version": "1.1",
  "proposal_id": "lsp-78901",
  "session_id": "sess-12345",
  "document_type": "word",
  "metadata": {
    "title": "Quarterly Business Review",
    "author": "Jane Doe",
    "theme": "corporate_blue",
    "mode": "ai_assist",
    "created_at": "2025-11-09T09:00:00Z"
  },
  "structure": [],
  "design_rationale": {},
  "warnings": [],
  "formatter_overrides": {}
}
```

### 4.1 Structure Array
Each entry represents a logical unit (section, page, or slide).
- `unit_id` (string): Unique identifier.
- `type` (enum): `section`, `page`, `slide`.
- `title` (string): Human-readable label.
- `template` (enum): For PPT (`title_slide`, `two_column`, etc.); for Word (`single_column`, `two_column`).
- `elements`: Ordered list of layout elements described below.
- `notes`: Optional instructions for reviewers or post-processing.

### 4.2 Layout Elements
Element object fields:
- `element_id` (string, required).
- `content_ref` (string): Links back to CIP content or computed asset.
- `role` (enum): `primary_text`, `supporting_text`, `visual`, `data_table`, `callout`.
- `type` (enum): `text`, `image`, `table`, `shape`, `chart`.
- `position`: Coordinates relative to page/slide.
  - `x`, `y`, `width`, `height` (float, inches).
  - `z_index` (integer) for stacking order.
- `grid`: Optional structure with `column_start`, `column_span`, `row_start`, `row_span`.
- `styling`: Includes `font`, `color`, `alignment`, `spacing`, `background`.
- `gestalt_rules`: Tags such as `hierarchy_level`, `proximity_group`, `similarity_family`.
- `behaviors`: Rendering hints (e.g., `shrink_to_fit`, `keep_with_next`, `allow_page_break`).

### 4.3 Styling Tokens
- `font`: `family`, `size_pt`, `weight`, `style`, `caps`.
- `color`: Foreground hex string; optional `background`.
- `spacing`: `margin_top`, `margin_bottom`, `margin_left`, `margin_right`, `line_height`.
- `borders`: `color`, `width_pt`, `style`.
- `lists`: For bullet or numbered lists (`style`, `indent_level`).
- `tables`: Column widths (inches), header styling, zebra striping settings.

### 4.4 Design Rationale
- `principles_applied`: Array of principles influencing this unit (`proximity`, `figure_ground`, `continuity`).
- `scores`: Numeric assessments (e.g., `hierarchy_clarity = 0.92`).
- `ai_contributions`: Notes on AI suggestions accepted or rejected.
- `warnings`: Items that required manual adjustment or where strict adherence was not possible.

### 4.5 Formatter Overrides
- Allows the formatter to adjust behavior via `suggested_scaling`, `fallback_template`, or `allowed_adjustments`.
- Example: `{ "text_overflow_policy": "shrink_font_to_min_10pt" }`.

## 5. Validation Rules
- `schema_version` must match formatter support; mismatched versions return `409 Conflict`.
- All element coordinates must remain within slide/page dimensions defined by formatter capabilities.
- `content_ref` must resolve to content or assets accessible to the formatter.
- Color values must be valid hex strings (`#RRGGBB`).
- Tables must define column widths whose sum plus inter-column spacing equals container width ±0.05 inches.
- `hierarchy_level` values must be between 1 and 5 inclusive.
- If `document_type = "presentation"`, element count per slide ≤ 12 to avoid clutter.

## 6. Error Semantics
- On validation failure, formatter responds with `422 Unprocessable Entity` including `errors[]` listing `element_id`, `field`, and `issue`.
- Soft warnings (e.g., `text_shrink_required`) returned in response metadata but do not fail rendering.
- If assets are missing, formatter returns `404 Not Found` with code `CONTENT_REF_MISSING`.

## 7. Versioning Strategy
- Semantic versioning: `major.minor`.
- Minor revisions allow additive changes (optional fields); major revisions require new endpoint or query parameter `schema_version`.
- Gestalt Design Engine can serve multiple versions by mapping to compatibility adapters before sending to formatter.

## 8. Observability
- Producer logs `proposal_id`, `document_type`, `unit_count`, `element_count`, `warnings`.
- Consumer logs validation outcomes and adjustments. Expose metrics: average element count per unit, frequency of fallback templates.
- Emit CloudEvents `layout.spec.created` and `layout.spec.validated`.

## 9. Security Considerations
- Payload encryption in transit; no sensitive data stored in plain text beyond operational retention.
- Include digital signature or HMAC over payload to ensure authenticity (header `X-Signature`).
- Strip human-readable text from logs unless debugging mode is explicitly enabled.

## 10. Future Enhancements
- Extend element definitions to support animations once rendering engine supports them.
- Provide diff metadata when LSPs are regenerated to highlight changes.
- Introduce reusable component references (`component_ref`) for frequently used layout patterns.

