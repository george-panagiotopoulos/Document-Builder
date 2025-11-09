"""
Pytest configuration and shared fixtures.

Provides test fixtures and utilities for all test modules.
"""

import pytest
from typing import Any


@pytest.fixture
def sample_content_blocks() -> list[dict[str, Any]]:
    """Sample content blocks for testing."""
    return [
        {
            "type": "heading",
            "level": 1,
            "sequence": 0,
            "text": "Test Document",
        },
        {
            "type": "paragraph",
            "level": 0,
            "sequence": 1,
            "text": "This is a test paragraph.",
        },
    ]


@pytest.fixture
def sample_design_intent() -> dict[str, Any]:
    """Sample design intent for testing."""
    return {
        "purpose": "report",
        "audience": "technical",
        "tone": "formal",
        "goals": ["clarity", "detail"],
    }


@pytest.fixture
def sample_cip(sample_content_blocks: list[dict[str, Any]], sample_design_intent: dict[str, Any]) -> dict[str, Any]:
    """Sample Content-Intent Package for testing."""
    return {
        "schema_version": "1.1",
        "session_id": "sess-test123",
        "submission_id": "subm-2025-11-09T12:00:00Z",
        "content": {
            "blocks": sample_content_blocks,
            "images": [],
        },
        "design_intent": sample_design_intent,
        "constraints": {
            "visual_density": "balanced",
        },
        "metadata": {
            "source_system": "cli",
        },
    }


@pytest.fixture
def sample_lsp() -> dict[str, Any]:
    """Sample Layout Specification Package for testing."""
    return {
        "schema_version": "1.1",
        "proposal_id": "lsp-test456",
        "session_id": "sess-test123",
        "document_type": "word",
        "metadata": {
            "title": "Test Document",
            "mode": "rule_only",
            "created_at": "2025-11-09T12:00:00Z",
        },
        "structure": [
            {
                "unit_id": "unit-1",
                "type": "page",
                "title": "Page 1",
                "template": "single_column",
                "elements": [],
            }
        ],
        "design_rationale": {
            "principles_applied": ["hierarchy", "alignment"],
            "scores": {"overall_quality_score": 0.85},
            "quality_grade": "good",
        },
        "warnings": [],
        "formatter_overrides": {},
    }
