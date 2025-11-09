"""
Gestalt principles implementation.

Provides computational algorithms for applying Gestalt design principles
including hierarchy, proximity, similarity, alignment, whitespace, and contrast.
"""

import math


class GestaltPrinciples:
    """Implementation of Gestalt design principles."""

    # Modular scale using perfect fourth ratio (1.333)
    BASE_SIZE = 11  # Base font size in points
    SCALE_RATIO = 1.333

    # Grid system configuration
    GRID_COLUMNS = 12
    GUTTER = 0.2  # inches
    MARGIN = 0.75  # inches

    # Color palette
    TEXT_COLORS = {
        1: "#1a1a1a",  # Primary headings - near black
        2: "#333333",  # Secondary headings - dark gray
        3: "#4a4a4a",  # Tertiary headings - medium gray
        4: "#333333",  # Body text - dark gray
        5: "#666666",  # Captions - light gray
    }

    def calculate_hierarchy_size(self, hierarchy_level: int) -> int:
        """
        Calculate font size based on hierarchy level using modular scale.

        Args:
            hierarchy_level: Level from 1 (most important) to 5 (least important)

        Returns:
            Font size in points
        """
        # Map hierarchy levels to scale exponents
        exponent_map = {
            1: 3,  # ~26pt
            2: 2,  # ~19pt
            3: 1,  # ~15pt
            4: 0,  # ~11pt
            5: -1,  # ~8pt
        }

        exponent = exponent_map.get(hierarchy_level, 0)
        size = self.BASE_SIZE * (self.SCALE_RATIO ** exponent)
        return int(round(size))

    def get_text_color(self, hierarchy_level: int) -> str:
        """
        Get text color for a hierarchy level.

        Args:
            hierarchy_level: Level from 1 to 5

        Returns:
            Hex color string
        """
        return self.TEXT_COLORS.get(hierarchy_level, self.TEXT_COLORS[4])

    def get_density_factor(self, visual_density: str) -> float:
        """
        Get spacing density factor.

        Args:
            visual_density: "tight", "balanced", or "airy"

        Returns:
            Density multiplier
        """
        density_factors = {
            "tight": 0.7,
            "balanced": 1.0,
            "airy": 1.5,
        }
        return density_factors.get(visual_density, 1.0)

    def calculate_spacing(
        self, hierarchy_level: int, density_factor: float
    ) -> tuple[float, float]:
        """
        Calculate vertical spacing before and after an element.

        Args:
            hierarchy_level: Element hierarchy level
            density_factor: Density multiplier from visual_density

        Returns:
            Tuple of (space_before, space_after) in inches
        """
        spacing_rules = {
            1: (1.0, 0.5),  # Title
            2: (0.75, 0.3),  # Heading
            3: (0.5, 0.25),  # Subheading
            4: (0.3, 0.3),  # Body
            5: (0.2, 0.2),  # Caption
        }

        base_before, base_after = spacing_rules.get(hierarchy_level, (0.3, 0.3))
        return (base_before * density_factor, base_after * density_factor)

    def calculate_contrast_ratio(
        self, foreground: str, background: str = "#ffffff"
    ) -> float:
        """
        Calculate WCAG contrast ratio between two colors.

        Args:
            foreground: Foreground color hex string
            background: Background color hex string

        Returns:
            Contrast ratio (1.0 to 21.0)
        """
        # Convert hex to RGB
        def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore

        # Calculate relative luminance
        def relative_luminance(rgb: tuple[int, int, int]) -> float:
            r, g, b = [x / 255.0 for x in rgb]
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        fg_rgb = hex_to_rgb(foreground)
        bg_rgb = hex_to_rgb(background)

        l1 = relative_luminance(fg_rgb)
        l2 = relative_luminance(bg_rgb)

        lighter = max(l1, l2)
        darker = min(l1, l2)

        return (lighter + 0.05) / (darker + 0.05)

    def snap_to_grid(self, x_position: float, width_in_columns: int) -> float:
        """
        Snap element to grid column.

        Args:
            x_position: Desired X position in inches
            width_in_columns: Number of columns to span

        Returns:
            Snapped X position in inches
        """
        column_width = self._calculate_column_width()
        column_positions = [
            self.MARGIN + i * (column_width + self.GUTTER) for i in range(self.GRID_COLUMNS)
        ]

        # Find closest column start
        snapped_x = min(column_positions, key=lambda cx: abs(cx - x_position))
        return snapped_x

    def snap_to_baseline(self, y_position: float, baseline_grid: float = 0.25) -> float:
        """
        Snap vertical position to baseline grid.

        Args:
            y_position: Desired Y position in inches
            baseline_grid: Baseline grid size in inches

        Returns:
            Snapped Y position in inches
        """
        return round(y_position / baseline_grid) * baseline_grid

    def _calculate_column_width(self, page_width: float = 10.0) -> float:
        """Calculate width of a single grid column."""
        usable_width = page_width - (2 * self.MARGIN)
        total_gutter = self.GUTTER * (self.GRID_COLUMNS - 1)
        return (usable_width - total_gutter) / self.GRID_COLUMNS
