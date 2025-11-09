"""
HTTP client for Document Formatter Service.

Handles communication with the Document Formatter API for document rendering.
"""

import httpx
from typing import Any
import logging

from services.content_intake.utils.config import settings

logger = logging.getLogger(__name__)


class FormatterClient:
    """Client for Document Formatter Service API."""

    def __init__(self, base_url: str | None = None, timeout: float = 60.0) -> None:
        """
        Initialize formatter client.

        Args:
            base_url: Base URL for Document Formatter API (defaults to config)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or settings.DOCUMENT_FORMATTER_URL
        self.timeout = timeout

    async def render_document(self, lsp: dict[str, Any]) -> dict[str, Any]:
        """
        Render Word document from Layout Specification Package.

        Args:
            lsp: Layout Specification Package dictionary

        Returns:
            Render job response with render_job_id and artifact_id

        Raises:
            httpx.HTTPError: If request fails
            ValueError: If response is invalid
        """
        url = f"{self.base_url}/v1/render/documents"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Submitting LSP to Document Formatter: {url}")
                response = await client.post(url, json={"layout_specification": lsp})
                response.raise_for_status()

                data = response.json()
                logger.info(
                    f"Document render job created: {data.get('render_job_id')} "
                    f"(status: {data.get('status')})"
                )
                return data

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Document Formatter returned error: {e.response.status_code} - {e.response.text}"
            )
            raise ValueError(
                f"Document Formatter rejected request: {e.response.status_code} - {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to Document Formatter: {e}")
            raise ValueError(f"Cannot reach Document Formatter at {self.base_url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error calling Document Formatter: {e}")
            raise

    async def render_presentation(self, lsp: dict[str, Any]) -> dict[str, Any]:
        """
        Render PowerPoint presentation from Layout Specification Package.

        Args:
            lsp: Layout Specification Package dictionary

        Returns:
            Render job response with render_job_id and artifact_id

        Raises:
            httpx.HTTPError: If request fails
            ValueError: If response is invalid
        """
        url = f"{self.base_url}/v1/render/presentations"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Submitting LSP to Document Formatter for PPTX: {url}")
                response = await client.post(url, json={"layout_specification": lsp})
                response.raise_for_status()

                data = response.json()
                logger.info(
                    f"Presentation render job created: {data.get('render_job_id')} "
                    f"(status: {data.get('status')})"
                )
                return data

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Document Formatter returned error: {e.response.status_code} - {e.response.text}"
            )
            raise ValueError(
                f"Document Formatter rejected request: {e.response.status_code} - {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to Document Formatter: {e}")
            raise ValueError(f"Cannot reach Document Formatter at {self.base_url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error calling Document Formatter: {e}")
            raise

