# Gestalt Design Engine Design

## 1. Purpose
The Gestalt Design Engine (Component B) converts normalized content and intent metadata into detailed layout specifications that embody Gestalt and information design principles. It combines deterministic rule systems with optional AI advisory to propose outline structures for Word documents and slide layouts for PowerPoint.

## 2. Key Responsibilities
- Interpret Content-Intent Packages (CIP) and derive semantic structure (sections, emphasis areas, visual density).
- Apply Gestalt principles (proximity, similarity, continuity, figure-ground, hierarchy) to assign sizing, positioning, and grouping directives.
- Produce a Layout Specification Package (LSP) suitable for direct consumption by formatter services.
- Offer dual modes: rule-based baseline and AI-enhanced hybrid with deterministic validation.
- Maintain traceable design rationale and scoring to support QA and auditing.

## 3. Architectural Overview
- **API Layer**: REST interface (`POST /v1/layout/proposals`) receiving CIP payloads and returning proposal IDs; `GET /v1/layout/proposals/{id}` for status and retrieval.
- **Content Analysis Module**: Performs linguistic and structural parsing, identifies content types, estimates importance weighting, and tags media assets.
- **Design Principles Engine**: Enforces configurable Gestalt rules, computes grids, spacing, and hierarchy metrics.
- **AI Advisory Module** (optional): Requests layout suggestions from LLM providers; operates under strict schemas and timeout constraints.
- **Validation and Harmonization Layer**: Merges AI suggestions with rule-based outputs, ensures feasibility within formatter capabilities, and resolves conflicts.
- **Specification Builder**: Serializes final LSP JSON, stores metadata, and exposes artifacts through persistence APIs.

## 4. Data Contracts
- **Input**: Content-Intent Package (`application/json`) defined in `ContentIntentInterfaceDesign.MD`.
- **Output**: Layout Specification Package (`application/json`) defined in `LayoutSpecificationInterfaceDesign.MD`, with references to generated Word outline and PowerPoint slide plans.
- **Metadata**: Design rationale (`principles_applied`, `confidence_scores`, `ai_mode`), timestamps, and cache keys for re-rendering.

## 5. Processing Stages
1. **Ingestion**: Validate CIP schema version, authenticate request scope `layout.generate`.
2. **Structural Parsing**: Build hierarchical representation (document tree) using heading levels, list structures, and semantic cues.
3. **Content Typing**: Categorize blocks (narrative, data-focused, persuasive, procedural) to tailor layout heuristics.
4. **Constraints Blending**: Merge global constraints (branding, density preference) with per-section directives; compute allowable template sets.
5. **Rule Application**: Calculate hierarchy scales, grid assignments, spacing, and color palette selections; generate baseline layout plan.
6. **AI Advisory (optional)**: Request high-level layout adjustments, e.g., section grouping or emphasis suggestions. Enforce deterministic review before acceptance.
7. **Validation**: Confirm compatibility with formatter capabilities (dimensions, template availability, color contrast). Create warning list for any soft violations.
8. **Specification Assembly**: Compose LSP with sections/pages, element coordinates, styling tokens, and rationale; store in persistence layer.

## 6. Gestalt Principles - Computational Algorithms

This section defines the specific algorithms, formulas, and measurable outputs for each Gestalt principle. These algorithms form the deterministic foundation of the design engine.

### 6.1 Proximity Principle

**Purpose**: Group related elements by spatial distance to create visual relationships.

**Algorithm**:
1. **Distance Calculation**: For each pair of elements, calculate Euclidean distance:
   ```
   distance = sqrt((x2 - x1)² + (y2 - y1)²)
   ```
   Where (x, y) represents the center point of each element.

2. **Adaptive Threshold**: Calculate threshold based on average element dimensions:
   ```
   avg_height = mean(all element heights)
   threshold = avg_height * 1.5  // 1.5x average height
   ```
   Minimum threshold: 0.3 inches. Maximum threshold: 2.0 inches.

3. **Clustering**: Apply single-linkage clustering:
   - Elements with distance < threshold belong to same group
   - Groups merge if any element from one group is within threshold of any element from another
   - Assign unique `proximity_group` ID to each cluster

4. **Spacing Rules**:
   - **Intra-group spacing**: Elements within same group have spacing multiplier = 1.0
   - **Inter-group spacing**: Elements from different groups have spacing multiplier = 2.5-3.0
   - **Group boundary**: Calculate bounding box for each group; ensure minimum 0.5 inch gap between group boundaries

**Measurable Outputs**:
- `proximity_group`: String identifier (e.g., "group-A", "group-B")
- `spacing_multiplier`: Float (1.0 for intra-group, 2.5-3.0 for inter-group)
- `group_center`: (x, y) coordinates of group centroid
- `group_size`: Number of elements in group

**Validation Criteria**:
- All elements must belong to exactly one proximity group
- Groups with single elements are allowed (isolated content)
- Maximum group size: 8 elements (larger groups should be subdivided)

### 6.2 Similarity Principle

**Purpose**: Elements with similar styling are perceived as related.

**Algorithm**:
1. **Style Family Classification**: Define style families based on content type and hierarchy:
   ```
   Style Families:
   - heading: {level-1, level-2, level-3}
   - body: {paragraph, list, caption}
   - emphasis: {quote, callout, highlight}
   ```

2. **Style Assignment Rules**:
   - **Heading Family**: 
     - Level 1: size=28pt, weight=bold, color=#1a1a1a
     - Level 2: size=22pt, weight=bold, color=#333333
     - Level 3: size=18pt, weight=semibold, color=#4a4a4a
   - **Body Family**:
     - Paragraph: size=11pt, weight=normal, color=#333333
     - List: size=11pt, weight=normal, color=#333333
     - Caption: size=9pt, weight=normal, color=#666666
   - **Emphasis Family**:
     - Quote: size=12pt, weight=italic, color=#555555
     - Callout: size=11pt, weight=medium, color=#0066cc

3. **Consistency Check**: For each style family, ensure:
   - All elements in same family use identical font family
   - Color variations within family ≤ 2 shades
   - Size variations follow hierarchy rules (no arbitrary sizes)

4. **Similarity Score**: Calculate consistency percentage:
   ```
   consistency_score = (elements_following_family_rules / total_elements_in_family) * 100
   ```
   Target: ≥95% consistency within each family.

**Measurable Outputs**:
- `style_family`: String identifier (e.g., "heading-1", "body-paragraph")
- `font_family`: String (e.g., "Arial", "Calibri")
- `font_size_pt`: Integer (points)
- `font_weight`: Enum (normal, medium, semibold, bold)
- `color_hex`: String (e.g., "#333333")
- `consistency_score`: Float (0.0-1.0)

**Validation Criteria**:
- All elements must belong to exactly one style family
- Consistency score ≥ 0.95 for each family
- No more than 3 distinct font families per document/slide deck

### 6.3 Visual Hierarchy Principle

**Purpose**: Size and positioning indicate importance.

**Algorithm**:
1. **Modular Scale**: Use perfect fourth ratio (1.333) for type scale:
   ```
   base_size = 11  // Base font size in points
   scale_ratio = 1.333
   
   hierarchy_sizes = {
       1: base_size * (scale_ratio ** 3),  // ~26pt
       2: base_size * (scale_ratio ** 2),  // ~19pt
       3: base_size * (scale_ratio ** 1),  // ~15pt
       4: base_size * (scale_ratio ** 0),  // ~11pt
       5: base_size * (scale_ratio ** -1)  // ~8pt
   }
   ```

2. **Hierarchy Level Assignment**:
   - Level 1: Document/slide title, primary headings
   - Level 2: Section headings, major subsections
   - Level 3: Subsection headings, important callouts
   - Level 4: Body text, standard paragraphs
   - Level 5: Captions, footnotes, fine print

3. **Spatial Hierarchy**: Calculate Y-position based on importance:
   ```
   def calculate_y_position(hierarchy_level, section_top, page_height):
       y_offsets = {
           1: section_top + 0.5,      // Title: near top
           2: section_top + 1.5,      // Subtitle
           3: section_top + 2.5,      // Section headers
           4: section_top + 3.0,      // Body content
           5: page_height - 1.0       // Captions: near bottom
       }
       return y_offsets.get(hierarchy_level, section_top + 3.0)
   ```

4. **Size Ratio Validation**: Ensure clear size relationships:
   ```
   min_ratio_between_levels = 1.15  // 15% minimum difference
   ```
   Adjacent hierarchy levels must differ by at least 15% in size.

**Measurable Outputs**:
- `hierarchy_level`: Integer (1-5, where 1 = most important)
- `font_size_pt`: Integer (calculated from hierarchy level)
- `size_ratio`: Float (ratio compared to base size)
- `vertical_position`: Float (Y-coordinate in inches)
- `hierarchy_clarity_score`: Float (0.0-1.0, measures size differentiation)

**Validation Criteria**:
- Hierarchy levels must be between 1 and 5
- Size ratios between adjacent levels ≥ 1.15
- Hierarchy clarity score ≥ 0.85
- No two elements at same hierarchy level should have >5% size difference

### 6.4 Alignment & Grid Principle

**Purpose**: Elements aligned to common grid create visual order.

**Algorithm**:
1. **Grid System Definition**: 12-column grid (standard responsive design):
   ```
   grid = {
       'columns': 12,
       'gutter': 0.2,      // inches between columns
       'margin': 0.75,     // inches (left and right)
       'baseline': 0.25    // inches (vertical baseline grid)
   }
   ```

2. **Column Width Calculation**:
   ```
   page_width = 10.0  // inches (PowerPoint slide width)
   usable_width = page_width - (2 * grid['margin'])
   total_gutter = grid['gutter'] * (grid['columns'] - 1)
   column_width = (usable_width - total_gutter) / grid['columns']
   ```

3. **Grid Snapping (X-axis)**:
   ```
   def snap_to_grid(x_position, width_in_columns):
       column_x = [
           grid['margin'] + i * (column_width + grid['gutter'])
           for i in range(grid['columns'])
       ]
       # Find closest column start
       snapped_x = min(column_x, key=lambda cx: abs(cx - x_position))
       return snapped_x
   ```

4. **Baseline Snapping (Y-axis)**:
   ```
   def snap_to_baseline(y_position):
       return round(y_position / grid['baseline']) * grid['baseline']
   ```

5. **Element Width Calculation**:
   ```
   element_width = (
       width_in_columns * column_width +
       (width_in_columns - 1) * grid['gutter']
   )
   ```

**Measurable Outputs**:
- `grid_column_start`: Integer (1-12)
- `grid_column_span`: Integer (1-12)
- `grid_row`: Integer (baseline-aligned row number)
- `baseline_aligned`: Boolean (true if Y-position aligns to baseline)
- `grid_compliance_score`: Float (0.0-1.0, percentage of elements aligned)

**Validation Criteria**:
- All elements must have valid `grid_column_start` and `grid_column_span`
- `grid_column_start + grid_column_span` ≤ 13
- Grid compliance score ≥ 0.90 (90% of elements aligned)
- Baseline alignment required for all text elements

### 6.5 Whitespace & Breathing Room

**Purpose**: Negative space improves readability and focus.

**Algorithm**:
1. **Density Factor**: Based on content density preference:
   ```
   density_factors = {
       'tight': 0.7,      // Academic papers, data-heavy
       'medium': 1.0,     // Standard business docs
       'airy': 1.5        // Marketing, presentations
   }
   base_factor = density_factors[content_density]
   ```

2. **Vertical Spacing (Based on Hierarchy)**:
   ```
   spacing_rules = {
       1: {  // Title
           'space_before': 1.0 * base_factor,
           'space_after': 0.5 * base_factor
       },
       2: {  // Heading
           'space_before': 0.75 * base_factor,
           'space_after': 0.3 * base_factor
       },
       3+: {  // Body
           'space_before': 0.3 * base_factor,
           'space_after': 0.3 * base_factor
       }
   }
   ```

3. **Line Spacing (Leading)**:
   ```
   if element.type == 'paragraph':
       line_spacing = font_size * 1.35  // 135% of font size
   else:
       line_spacing = font_size * 1.2   // 120% of font size
   ```
   Minimum line spacing: 1.15x font size. Maximum: 1.5x font size.

4. **Margin Calculation**:
   ```
   margin_multiplier = 2.0 - (hierarchy_level * 0.2)
   element_margin = 0.5 * margin_multiplier * base_factor
   ```
   More important elements get more breathing room.

**Measurable Outputs**:
- `space_before`: Float (inches)
- `space_after`: Float (inches)
- `line_spacing`: Float (points or multiplier)
- `margin`: Float (inches, external whitespace)
- `whitespace_ratio`: Float (whitespace area / total area)

**Validation Criteria**:
- Line spacing between 1.15x and 1.5x font size
- Whitespace ratio ≥ 0.20 (20% of page/slide should be whitespace)
- Minimum space_before/after: 0.1 inches
- Maximum space_before/after: 2.0 inches

### 6.6 Color & Contrast

**Purpose**: Ensure readability and visual emphasis.

**Algorithm**:
1. **Color Palette Generation**: From brand primary color:
   ```
   def generate_palette(primary_color_hex):
       # Convert to HSL
       h, s, l = rgb_to_hsl(hex_to_rgb(primary_color_hex))
       
       palette = {
           'primary': primary_color_hex,
           'primary_dark': hsl_to_rgb(h, s, l * 0.7),
           'primary_light': hsl_to_rgb(h, s * 0.3, 0.95),
           'text_primary': '#1a1a1a',      // Near black
           'text_secondary': '#4a4a4a',    // Medium gray
           'text_tertiary': '#767676',      // Light gray
           'background': '#ffffff',
           'background_alt': '#f5f5f5'
       }
       return palette
   ```

2. **Contrast Ratio Calculation** (WCAG AA compliance):
   ```
   def calculate_contrast_ratio(foreground, background):
       # Calculate relative luminance
       l1 = relative_luminance(foreground)
       l2 = relative_luminance(background)
       
       # Contrast ratio formula
       lighter = max(l1, l2)
       darker = min(l1, l2)
       ratio = (lighter + 0.05) / (darker + 0.05)
       return ratio
   ```

3. **Contrast Validation**:
   - Normal text: Contrast ratio ≥ 4.5:1 (WCAG AA)
   - Large text (18pt+): Contrast ratio ≥ 3:1 (WCAG AA)
   - If contrast insufficient, adjust color automatically:
     ```
     if contrast_ratio < required_ratio:
         adjusted_color = darken_or_lighten(color, required_ratio)
     ```

4. **Color Application Rules**:
   - Primary color: Headings, callouts, emphasis
   - Text colors: Use text_primary for body, text_secondary for captions
   - Background: White for documents, white or brand_light for slides

**Measurable Outputs**:
- `color_palette`: Object with hex color strings
- `contrast_ratio`: Float (foreground vs background)
- `accessibility_level`: String ("WCAG AA" or "WCAG AAA")
- `color_harmony_score`: Float (0.0-1.0, measures color relationships)

**Validation Criteria**:
- All text must meet WCAG AA contrast requirements (4.5:1)
- Color palette must have at least 3 distinct colors
- Maximum 5 colors in palette (avoid color overload)
- Contrast ratios validated for all text/background combinations

### 6.7 Design Quality Scoring

**Purpose**: Quantify how well a layout adheres to Gestalt principles.

**Algorithm**:
1. **Principle Scores**: Calculate score for each principle (0.0-1.0):
   - Proximity score: Percentage of elements in appropriate groups
   - Similarity score: Consistency within style families
   - Hierarchy score: Clarity of size relationships
   - Alignment score: Grid compliance percentage
   - Whitespace score: Adequacy of negative space
   - Contrast score: WCAG compliance percentage

2. **Overall Quality Score**:
   ```
   weights = {
       'proximity': 0.15,
       'similarity': 0.15,
       'hierarchy': 0.25,
       'alignment': 0.20,
       'whitespace': 0.15,
       'contrast': 0.10
   }
   
   overall_score = sum(principle_score * weight for principle, weight in weights.items())
   ```

3. **Quality Thresholds**:
   - Excellent: ≥ 0.90
   - Good: 0.75 - 0.89
   - Acceptable: 0.60 - 0.74
   - Needs Improvement: < 0.60

**Measurable Outputs**:
- `principle_scores`: Object with scores for each principle
- `overall_quality_score`: Float (0.0-1.0)
- `quality_grade`: String ("excellent", "good", "acceptable", "needs_improvement")
- `improvement_suggestions`: Array of actionable recommendations

**Validation Criteria**:
- Overall quality score must be calculated for every layout
- Scores stored in LSP `design_rationale.scores` field
- Layouts with score < 0.60 should trigger warnings

## 7. Rule-Based Layout Generation

### 7.1 Template Selection Decision Tree

**PowerPoint Templates**:
```
if is_first_section:
    return 'title_slide'
elif has_image and text_count <= 2:
    return 'image_with_caption'
elif has_list and not has_image:
    return 'bullet_list'
elif has_image and text_count > 2:
    return 'two_column_image_text'
elif text_count > 5:
    return 'text_heavy'
else:
    return 'standard_content'
```

**Word Templates**:
```
if has_many_images:
    return 'two_column'
elif has_tables:
    return 'single_column_with_tables'
elif text_density == 'high':
    return 'single_column'
else:
    return 'single_column'
```

### 7.2 Rule Precedence and Conflict Resolution

**Priority Order** (highest to lowest):
1. **Accessibility Rules**: Contrast, alt text (non-negotiable)
2. **Formatter Capabilities**: Template availability, dimension limits
3. **Hierarchy Rules**: Size relationships, importance ordering
4. **Alignment Rules**: Grid compliance
5. **Spacing Rules**: Whitespace, proximity
6. **Styling Rules**: Colors, fonts (most flexible)

**Conflict Resolution**:
- When rules conflict, higher priority rule wins
- Log conflict and resolution in `design_rationale.warnings`
- Apply automatic adjustments when possible
- Flag for manual review if resolution unclear

### 7.3 AI Integration and Merging Strategy

**AI Advisory Process**:
1. Generate rule-based layout first (baseline)
2. Request AI suggestions for:
   - High-level structure (section breaks, slide count)
   - Template selection per section
   - Emphasis recommendations (which elements to highlight)
3. Validate AI suggestions against:
   - Formatter capabilities
   - Gestalt principle rules
   - Accessibility requirements
4. Merge strategies:
   - **Hybrid Mode**: Use AI for structure/templates, rules for styling/positioning
   - **AI Full Mode**: Use AI suggestions, validate against rules, apply corrections
   - **Rule Only Mode**: Ignore AI, use pure rule-based output

**Validation of AI Output**:
- Check all element positions fit within page/slide bounds
- Verify contrast ratios meet WCAG requirements
- Ensure template names exist in formatter registry
- Validate color values are valid hex codes
- Confirm hierarchy levels are between 1-5

**Fallback Behavior**:
- If AI timeout: Use rule-based layout, set `ai_fallback=true`
- If AI invalid: Correct violations, use corrected version
- If AI unavailable: Always fall back to rule-based (never fail completely)

## 8. REST API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/layout/proposals` | Submit a CIP to generate Word and/or PowerPoint layout proposals; returns `proposal_id`. |
| `GET` | `/v1/layout/proposals/{proposal_id}` | Retrieve proposal status (`queued`, `processing`, `complete`, `failed`) and metadata. |
| `GET` | `/v1/layout/proposals/{proposal_id}/spec` | Download the finalized LSP JSON and accompanying rationale report. |
| `POST` | `/v1/layout/proposals/{proposal_id}/actions/recompute` | Re-run layout generation using an updated constraint profile. |

## 7. AI Integration Strategy
- **Modes**: `rule_only`, `ai_assist`, `ai_full` (default `ai_assist`).
- **Providers**: Configurable via environment; support for OpenAI, Anthropic, or internal models accessed through a common abstraction.
- **Safety Controls**: Schema-constrained prompts, maximum latency thresholds (3 seconds), deterministic fallback when AI unavailable.
- **Explainability**: Capture AI recommendations and include reasoning strings in the LSP `design_rationale` section.

## 8. Persistence and Caching
- Store canonical LSP documents in PostgreSQL JSONB columns with indexing on `proposal_id` and `session_id`.
- Maintain cache entries keyed by hash of (content fingerprint, constraint profile, mode) to enable idempotent recomputation.
- Persist AI prompts and responses in a secure audit store for traceability (subject to privacy policies).

## 9. Scaling and Performance
- Stateless compute nodes; horizontal scale via container orchestration.
- Separate worker pool for AI-enhanced mode to isolate latency impact.
- Target processing latency: <2 seconds for rule-only proposals, <6 seconds with AI assistance.
- Utilize concurrency controls to prevent over-saturation of LLM provider quotas.

## 10. Observability and Monitoring
- Emit structured events for each processing stage (`analysis_started`, `rules_applied`, `ai_consulted`, `spec_persisted`).
- Metrics: proposal latency, AI usage rate, validation warning counts, cache hit ratios.
- Distributed tracing with spans covering external AI calls and heavy computations.

## 11. Security Considerations
- Enforce JWT scope `layout.generate` for POST requests; read scopes for GET endpoints.
- Sanitize content before AI calls (mask sensitive tokens based on configurable rules).
- Encrypt stored layout artifacts and design rationale.
- Redact AI transcripts when exporting logs; require privileged access for debugging.

## 12. Failure Handling
- **Validation failure**: Return `400 Bad Request` with structured error codes; log rule violation details.
- **AI timeout**: Emit warning, fall back to rule-only output, set status flag `ai_fallback=true`.
- **Persistence failure**: Retry with exponential backoff; if unrecoverable, mark proposal `failed` with correlation ID.
- **Compatibility breach**: Flag as warning when layout exceeds formatter capabilities; auto-adjust or request human review depending on severity.

## 13. Roadmap Considerations
- Extend Gestalt rules with custom brand modules and region-specific typographic rules.
- Introduce reinforcement learning using user feedback on accepted layouts.
- Add scenario-specific templates (e.g., financial reports, product launch decks).

