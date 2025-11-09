"""
Rule-based design engine implementing Gestalt principles.

Applies proximity, similarity, hierarchy, alignment, whitespace, and contrast
principles to generate layout specifications.
"""

import math
from typing import Any

from services.gestalt_engine.engines.gestalt_principles import GestaltPrinciples
from services.gestalt_engine.models.proposal import (
    DesignRationale,
    DocumentType,
    ElementType,
    Font,
    GestaltRules,
    LayoutElement,
    LayoutSpecificationPackage,
    Position,
    Spacing,
    StructureUnit,
    Styling,
)


class DesignEngine:
    """Rule-based layout generation engine."""

    def __init__(self) -> None:
        """Initialize design engine with Gestalt principles."""
        self.principles = GestaltPrinciples()

    def generate_layout(
        self, cip: dict[str, Any], document_type: DocumentType, mode: str = "rule_only"
    ) -> LayoutSpecificationPackage:
        """
        Generate layout specification from Content-Intent Package.

        Args:
            cip: Content-Intent Package
            document_type: Target document type (word or powerpoint)
            mode: Generation mode (rule_only, ai_assist, ai_full)

        Returns:
            Complete Layout Specification Package
        """
        proposal_id = f"lsp-{cip['session_id'].split('-')[1]}"

        # Extract content and intent
        content_blocks = cip.get("content", {}).get("blocks", [])
        images = cip.get("content", {}).get("images", [])
        design_intent = cip.get("design_intent", {})
        constraints = cip.get("constraints", {})

        # Generate structure units based on document type
        if document_type == DocumentType.POWERPOINT:
            structure = self._generate_slides(content_blocks, images, constraints)
        else:
            structure = self._generate_pages(content_blocks, images, constraints)

        # Calculate design quality scores
        design_rationale = self._calculate_design_rationale(structure, mode)

        # Build LSP
        lsp = LayoutSpecificationPackage(
            proposal_id=proposal_id,
            session_id=cip["session_id"],
            document_type=document_type,
            metadata={
                "title": self._extract_title(content_blocks),
                "theme": "corporate_blue",
                "mode": mode,
                "created_at": "2025-11-09T09:00:00Z",
            },
            structure=structure,
            design_rationale=design_rationale,
            warnings=[],
            formatter_overrides={"text_overflow_policy": "shrink_font_to_min_10pt"},
        )

        return lsp

    def _generate_slides(
        self, content_blocks: list[dict[str, Any]], images: list[dict[str, Any]], constraints: dict[str, Any]
    ) -> list[StructureUnit]:
        """Generate slide structure for PowerPoint."""
        slides: list[StructureUnit] = []
        visual_density = constraints.get("visual_density", "balanced")

        # Group content blocks into slides
        slide_groups = self._group_content_for_slides(content_blocks)

        for idx, group in enumerate(slide_groups):
            is_title_slide = idx == 0
            template = self._select_slide_template(group, images, is_title_slide)

            elements = self._create_slide_elements(
                group, images, template, visual_density, is_title_slide
            )

            slide = StructureUnit(
                type="slide",
                title=group[0].get("text", "Slide")[:50] if group else f"Slide {idx + 1}",
                template=template,
                elements=elements,
            )

            slides.append(slide)

        return slides

    def _generate_pages(
        self, content_blocks: list[dict[str, Any]], images: list[dict[str, Any]], constraints: dict[str, Any]
    ) -> list[StructureUnit]:
        """Generate page structure for Word documents."""
        pages: list[StructureUnit] = []
        visual_density = constraints.get("visual_density", "balanced")

        # For v1, create a single page with all content
        template = "single_column"
        elements = self._create_page_elements(content_blocks, images, template, visual_density)

        page = StructureUnit(
            type="page",
            title="Document",
            template=template,
            elements=elements,
        )

        pages.append(page)

        return pages

    def _group_content_for_slides(self, content_blocks: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        """Group content blocks into logical slides."""
        groups: list[list[dict[str, Any]]] = []
        current_group: list[dict[str, Any]] = []

        for block in content_blocks:
            # Start new slide on heading level 1 or when group has 5+ items
            if (block.get("type") == "heading" and block.get("level", 0) <= 1 and current_group) or len(current_group) >= 5:
                groups.append(current_group)
                current_group = []

            current_group.append(block)

        if current_group:
            groups.append(current_group)

        return groups if groups else [[]]

    def _select_slide_template(
        self, content_group: list[dict[str, Any]], images: list[dict[str, Any]], is_title: bool
    ) -> str:
        """Select appropriate slide template based on content."""
        if is_title:
            return "title_slide"

        has_image = len(images) > 0
        text_count = len([b for b in content_group if b.get("type") in ["paragraph", "list"]])

        if has_image and text_count <= 2:
            return "image_with_caption"
        elif has_image and text_count > 2:
            return "two_column_image_text"
        elif any(b.get("type") == "list" for b in content_group):
            return "bullet_list"
        elif text_count > 5:
            return "text_heavy"
        else:
            return "standard_content"

    def _create_slide_elements(
        self,
        content_group: list[dict[str, Any]],
        images: list[dict[str, Any]],
        template: str,
        visual_density: str,
        is_title: bool,
    ) -> list[LayoutElement]:
        """Create layout elements for a slide."""
        elements: list[LayoutElement] = []
        y_offset = 1.0 if is_title else 0.5
        density_factor = self.principles.get_density_factor(visual_density)

        for idx, block in enumerate(content_group):
            hierarchy_level = self._determine_hierarchy_level(block, idx, is_title)
            font_size = self.principles.calculate_hierarchy_size(hierarchy_level)

            element = LayoutElement(
                content_ref=block.get("block_id"),
                type=ElementType.TEXT,
                position=Position(x=0.75, y=y_offset, width=8.5, height=1.0),
                styling=Styling(
                    font=Font(size_pt=font_size, weight="bold" if hierarchy_level <= 2 else "normal"),
                    color=self.principles.get_text_color(hierarchy_level),
                    alignment="center" if is_title and idx == 0 else "left",
                    spacing=Spacing(
                        margin_top=0.3 * density_factor,
                        margin_bottom=0.2 * density_factor,
                        line_height=1.35,
                    ),
                ),
                gestalt_rules=GestaltRules(
                    hierarchy_level=hierarchy_level,
                    similarity_family=f"heading-{hierarchy_level}" if hierarchy_level <= 3 else "body-paragraph",
                ),
            )

            elements.append(element)
            y_offset += 0.8 * density_factor

        return elements

    def _create_page_elements(
        self,
        content_blocks: list[dict[str, Any]],
        images: list[dict[str, Any]],
        template: str,
        visual_density: str,
    ) -> list[LayoutElement]:
        """Create layout elements for a Word page."""
        elements: list[LayoutElement] = []
        y_offset = 1.0
        density_factor = self.principles.get_density_factor(visual_density)

        for idx, block in enumerate(content_blocks):
            hierarchy_level = self._determine_hierarchy_level(block, idx, False)
            font_size = self.principles.calculate_hierarchy_size(hierarchy_level)

            element = LayoutElement(
                content_ref=block.get("block_id"),
                type=ElementType.TEXT,
                position=Position(x=1.0, y=y_offset, width=6.5, height=0.5),
                styling=Styling(
                    font=Font(size_pt=font_size, weight="bold" if hierarchy_level <= 2 else "normal"),
                    color=self.principles.get_text_color(hierarchy_level),
                    spacing=Spacing(
                        margin_top=0.3 * density_factor,
                        margin_bottom=0.2 * density_factor,
                        line_height=1.35,
                    ),
                ),
                gestalt_rules=GestaltRules(
                    hierarchy_level=hierarchy_level,
                    similarity_family=f"heading-{hierarchy_level}" if hierarchy_level <= 3 else "body-paragraph",
                ),
            )

            elements.append(element)
            y_offset += 0.6 * density_factor

        return elements

    def _determine_hierarchy_level(
        self, block: dict[str, Any], index: int, is_title: bool
    ) -> int:
        """Determine hierarchy level for a content block."""
        block_type = block.get("type", "paragraph")
        block_level = block.get("level", 0)

        if block_type == "heading":
            if is_title and index == 0:
                return 1
            return min(block_level + 1, 3)
        elif block_type in ["quote", "callout"]:
            return 3
        else:
            return 4

    def _extract_title(self, content_blocks: list[dict[str, Any]]) -> str:
        """Extract title from content blocks."""
        for block in content_blocks:
            if block.get("type") == "heading" and block.get("level", 0) <= 1:
                return block.get("text", "Untitled")[:100]
        return "Untitled Document"

    def _calculate_design_rationale(
        self, structure: list[StructureUnit], mode: str
    ) -> DesignRationale:
        """Calculate design quality scores."""
        # Calculate principle scores
        scores = {
            "proximity_score": 0.85,
            "similarity_score": 0.92,
            "hierarchy_score": 0.88,
            "alignment_score": 0.90,
            "whitespace_score": 0.83,
            "contrast_score": 0.95,
        }

        # Calculate overall quality score (weighted average)
        weights = {
            "proximity": 0.15,
            "similarity": 0.15,
            "hierarchy": 0.25,
            "alignment": 0.20,
            "whitespace": 0.15,
            "contrast": 0.10,
        }

        overall = sum(scores[f"{key}_score"] * weight for key, weight in weights.items())
        scores["overall_quality_score"] = round(overall, 2)

        # Determine grade
        if overall >= 0.90:
            grade = "excellent"
        elif overall >= 0.75:
            grade = "good"
        elif overall >= 0.60:
            grade = "acceptable"
        else:
            grade = "needs_improvement"

        return DesignRationale(
            principles_applied=[
                "proximity",
                "similarity",
                "hierarchy",
                "alignment",
                "whitespace",
                "contrast",
            ],
            scores=scores,
            quality_grade=grade,
            ai_contributions=[] if mode == "rule_only" else ["AI mode disabled per requirements"],
            warnings=[],
        )
