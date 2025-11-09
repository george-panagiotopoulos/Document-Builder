"""
Sample content for end-to-end testing.

Contains 2 text blocks and 2 image references for testing document generation.
"""

# Sample text content
SAMPLE_TEXT_BLOCKS = [
    {
        "block_id": "block-001",
        "type": "heading",
        "level": 1,
        "sequence": 0,
        "text": "Quarterly Business Review - Q4 2024",
        "language": "en",
    },
    {
        "block_id": "block-002",
        "type": "paragraph",
        "level": 0,
        "sequence": 1,
        "text": "Our team achieved remarkable growth this quarter with revenue increasing by 45% year-over-year. Key highlights include expansion into three new markets, successful product launches, and improved customer satisfaction scores across all segments.",
        "language": "en",
    },
]

# Sample image references (using placeholder image service)
SAMPLE_IMAGES = [
    {
        "image_id": "img-001",
        "uri": "https://via.placeholder.com/800x600/0066cc/ffffff?text=Revenue+Growth",
        "format": "png",
        "width_px": 800,
        "height_px": 600,
        "alt_text": "Revenue growth chart showing 45% increase",
        "content_role": "data_visualization",
    },
    {
        "image_id": "img-002",
        "uri": "https://via.placeholder.com/800x600/28a745/ffffff?text=Market+Expansion",
        "format": "png",
        "width_px": 800,
        "height_px": 600,
        "alt_text": "Map showing new market regions",
        "content_role": "illustration",
    },
]

# Design intent for business presentation
SAMPLE_DESIGN_INTENT = {
    "purpose": "presentation",
    "audience": "executive",
    "tone": "formal",
    "goals": ["clarity", "impact"],
}

# Layout constraints
SAMPLE_CONSTRAINTS = {
    "visual_density": "balanced",
    "max_pages": 10,
    "color_scheme": "corporate",
}

# Complete session request
def get_sample_session_request():
    """Get a complete session request with all sample data."""
    return {
        "content_blocks": SAMPLE_TEXT_BLOCKS,
        "images": SAMPLE_IMAGES,
        "design_intent": SAMPLE_DESIGN_INTENT,
        "constraints": SAMPLE_CONSTRAINTS,
    }


# Alternative sample for Word document
SAMPLE_DOCUMENT_BLOCKS = [
    {
        "block_id": "block-doc-001",
        "type": "heading",
        "level": 1,
        "sequence": 0,
        "text": "Technical Specification Document",
        "language": "en",
    },
    {
        "block_id": "block-doc-002",
        "type": "paragraph",
        "level": 0,
        "sequence": 1,
        "text": "This document outlines the technical specifications for the new API integration platform. The system is designed to handle high-volume data processing with sub-second response times and 99.9% uptime guarantee.",
        "language": "en",
    },
]

SAMPLE_DOCUMENT_INTENT = {
    "purpose": "report",
    "audience": "technical",
    "tone": "formal",
    "goals": ["clarity", "completeness"],
}
