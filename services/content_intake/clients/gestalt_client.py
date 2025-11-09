"""
HTTP client for Gestalt Design Engine.

Handles communication with the Gestalt Design Engine API for layout generation.
"""

import httpx
from typing import Any
import logging

from services.content_intake.utils.config import settings

logger = logging.getLogger(__name__)


class GestaltClient:
    """Client for Gestalt Design Engine API."""

    def __init__(self, base_url: str | None = None, timeout: float = 30.0) -> None:
        """
        Initialize Gestalt client.

        Args:
            base_url: Base URL for Gestalt Engine API (defaults to config)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or settings.GESTALT_ENGINE_URL
        self.timeout = timeout

    async def create_proposal(
        self, cip: dict[str, Any], idempotency_key: str | None = None
    ) -> dict[str, Any]:
        """
        Submit Content-Intent Package to Gestalt Engine for layout generation.

        Args:
            cip: Content-Intent Package (CIP) dictionary
            idempotency_key: Optional idempotency key for request deduplication

        Returns:
            Proposal response with proposal_id and status

        Raises:
            httpx.HTTPError: If request fails
            ValueError: If response is invalid
        """
        url = f"{self.base_url}/layout/proposals"

        headers = {"Content-Type": "application/json"}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Submitting CIP to Gestalt Engine: {url}")
                response = await client.post(url, json=cip, headers=headers)
                response.raise_for_status()

                data = response.json()
                logger.info(
                    f"Gestalt proposal created: {data.get('proposal_id')} "
                    f"(status: {data.get('status')})"
                )
                return data

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Gestalt Engine returned error: {e.response.status_code} - {e.response.text}"
            )
            raise ValueError(
                f"Gestalt Engine rejected request: {e.response.status_code} - {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to Gestalt Engine: {e}")
            raise ValueError(f"Cannot reach Gestalt Engine at {self.base_url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error calling Gestalt Engine: {e}")
            raise

    async def get_proposal_status(self, proposal_id: str) -> dict[str, Any]:
        """
        Get proposal status from Gestalt Engine.

        Args:
            proposal_id: Proposal ID to check

        Returns:
            Proposal status response

        Raises:
            httpx.HTTPError: If request fails
        """
        url = f"{self.base_url}/layout/proposals/{proposal_id}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Proposal {proposal_id} not found")
            logger.error(f"Gestalt Engine returned error: {e.response.status_code}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to Gestalt Engine: {e}")
            raise ValueError(f"Cannot reach Gestalt Engine at {self.base_url}: {e}")

    async def get_specification(self, proposal_id: str) -> dict[str, Any]:
        """
        Download layout specification from Gestalt Engine.

        Args:
            proposal_id: Proposal ID

        Returns:
            Layout Specification Package (LSP)

        Raises:
            httpx.HTTPError: If request fails
        """
        url = f"{self.base_url}/layout/proposals/{proposal_id}/spec"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Specification for proposal {proposal_id} not found")
            logger.error(f"Gestalt Engine returned error: {e.response.status_code}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to Gestalt Engine: {e}")
            raise ValueError(f"Cannot reach Gestalt Engine at {self.base_url}: {e}")

    def build_cip(
        self,
        session_id: str,
        content_blocks: list[dict[str, Any]],
        images: list[dict[str, Any]],
        design_intent: dict[str, Any],
        constraints: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build Content-Intent Package (CIP) from session data.

        Args:
            session_id: Session ID
            content_blocks: List of content blocks
            images: List of image assets
            design_intent: Design intent configuration
            constraints: Layout constraints

        Returns:
            Content-Intent Package dictionary
        """
        cip = {
            "schema_version": "1.1",
            "session_id": session_id,
            "content": {
                "blocks": [
                    {
                        "block_id": block["block_id"],
                        "type": block["type"],
                        "level": block.get("level", 0),
                        "sequence": block["sequence"],
                        "text": block["text"],
                        "language": block.get("language", "en"),
                        "detected_role": block.get("detected_role"),
                        "metrics": block.get("metrics", {}),
                    }
                    for block in content_blocks
                ],
                "images": [
                    {
                        "image_id": image["image_id"],
                        "uri": image["uri"],
                        "format": image["format"],
                        "width_px": image["width_px"],
                        "height_px": image["height_px"],
                        "alt_text": image.get("alt_text"),
                        "content_role": image.get("content_role"),
                        "dominant_palette": image.get("dominant_palette", []),
                    }
                    for image in images
                ],
            },
            "design_intent": design_intent,
            "constraints": constraints,
        }

        return cip
