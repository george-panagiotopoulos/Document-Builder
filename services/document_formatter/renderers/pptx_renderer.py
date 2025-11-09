"""PowerPoint presentation renderer using python-pptx."""

from typing import Any
from uuid import uuid4
from pathlib import Path
import logging

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

logger = logging.getLogger(__name__)


class PowerPointRenderer:
    """Renders PowerPoint presentations from Layout Specification Packages."""

    def __init__(self, output_dir: str = "artifacts") -> None:
        """
        Initialize PowerPoint renderer.

        Args:
            output_dir: Directory to save generated presentations
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def render(self, lsp: dict[str, Any]) -> str:
        """
        Render PowerPoint presentation from LSP.

        Args:
            lsp: Layout Specification Package

        Returns:
            Artifact ID for the generated presentation
        """
        # Extract metadata
        metadata = lsp.get("metadata", {})
        structure = lsp.get("structure", [])
        proposal_id = lsp.get("proposal_id", "unknown")
        session_id = lsp.get("session_id", "unknown")

        # Create presentation
        prs = Presentation()

        # Set presentation dimensions to 16:9
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)

        title = metadata.get("title", "Untitled Presentation")

        logger.info(f"Rendering PowerPoint presentation: {title} with {len(structure)} slides")

        # Iterate through structure units (slides)
        for unit_idx, unit in enumerate(structure):
            unit_type = unit.get("type", "slide")
            unit_title = unit.get("title")
            template = unit.get("template", "standard_content")
            elements = unit.get("elements", [])

            # Select slide layout based on template
            slide_layout = self._select_layout(prs, template, unit_idx == 0)

            # Add slide
            slide = prs.slides.add_slide(slide_layout)

            # Render elements on slide
            await self._render_slide_elements(slide, elements, unit_title, lsp)

        # Generate artifact ID and save
        artifact_id = f"artifact-pptx-{uuid4().hex[:8]}"
        output_path = self.output_dir / f"{artifact_id}.pptx"

        prs.save(str(output_path))

        logger.info(f"PowerPoint presentation saved: {output_path} (artifact_id: {artifact_id})")

        return artifact_id

    def _select_layout(self, prs: Presentation, template: str, is_title: bool):
        """
        Select appropriate slide layout.

        Args:
            prs: Presentation instance
            template: Template name from LSP
            is_title: Whether this is the title slide

        Returns:
            Slide layout
        """
        # python-pptx default layouts:
        # 0 = Title Slide
        # 1 = Title and Content
        # 5 = Title Only
        # 6 = Blank

        if is_title or template == "title_slide":
            return prs.slide_layouts[0]  # Title Slide
        elif template in ["bullet_list", "standard_content"]:
            return prs.slide_layouts[1]  # Title and Content
        elif template == "title_only":
            return prs.slide_layouts[5]  # Title Only
        else:
            return prs.slide_layouts[6]  # Blank

    async def _render_slide_elements(
        self, slide, elements: list[dict[str, Any]], slide_title: str | None, lsp: dict[str, Any]
    ) -> None:
        """
        Render elements on a slide.

        Args:
            slide: Slide object
            elements: List of layout elements
            slide_title: Optional slide title
            lsp: Full LSP for content resolution
        """
        # Add title if present
        if slide_title and slide.shapes.title:
            slide.shapes.title.text = slide_title

        # For simplicity in v1, add text boxes for each element
        # In production, would use precise positioning from LSP
        for idx, element in enumerate(elements):
            element_type = element.get("type", "text")
            content_ref = element.get("content_ref")
            position = element.get("position", {})
            styling = element.get("styling", {})
            gestalt_rules = element.get("gestalt_rules", {})

            # Resolve content
            content_text = self._resolve_content(content_ref, lsp)

            if not content_text:
                continue

            if element_type == "text":
                # Get position (convert from LSP inches to python-pptx)
                left = Inches(position.get("x", 1.0))
                top = Inches(position.get("y", 1.5 + idx * 0.8))
                width = Inches(position.get("width", 8.5))
                height = Inches(position.get("height", 0.5))

                # Add text box
                textbox = slide.shapes.add_textbox(left, top, width, height)
                text_frame = textbox.text_frame
                text_frame.text = content_text

                # Apply styling
                self._apply_text_styling(text_frame, styling, gestalt_rules)

    def _resolve_content(self, content_ref: str | None, lsp: dict[str, Any]) -> str | None:
        """Resolve content text from content_ref."""
        if not content_ref:
            return None

        # In real implementation, would fetch from CIP or database
        # For v1, use content_ref as placeholder
        return f"[Content: {content_ref}]"

    def _apply_text_styling(
        self, text_frame, styling: dict[str, Any], gestalt_rules: dict[str, Any]
    ) -> None:
        """
        Apply styling to text frame.

        Args:
            text_frame: TextFrame object
            styling: Styling configuration
            gestalt_rules: Gestalt rules with hierarchy info
        """
        paragraph = text_frame.paragraphs[0]

        # Font styling
        font_config = styling.get("font", {})
        if font_config and paragraph.runs:
            font = paragraph.runs[0].font
            if "size_pt" in font_config:
                font.size = Pt(font_config["size_pt"])
            if "weight" in font_config and font_config["weight"] == "bold":
                font.bold = True

        # Color
        color_hex = styling.get("color")
        if color_hex and color_hex.startswith("#") and paragraph.runs:
            rgb = self._hex_to_rgb(color_hex)
            paragraph.runs[0].font.color.rgb = RGBColor(*rgb)

        # Alignment
        alignment_map = {
            "left": PP_ALIGN.LEFT,
            "center": PP_ALIGN.CENTER,
            "right": PP_ALIGN.RIGHT,
        }
        alignment = styling.get("alignment", "left")
        paragraph.alignment = alignment_map.get(alignment, PP_ALIGN.LEFT)

    def _hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
