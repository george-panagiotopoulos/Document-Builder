"""
Workflow orchestrator for document generation.

Coordinates sequential API calls across Content Intake, Gestalt Design Engine,
and Document Formatter services with retry logic and error handling.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

import httpx
from rich.progress import Progress, TaskID

from services.user_agent.workflow.state_machine import WorkflowState, WorkflowStateMachine
from services.user_agent.utils.config import settings


class WorkflowOrchestrator:
    """Orchestrates the end-to-end document generation workflow."""

    def __init__(self) -> None:
        """Initialize orchestrator with HTTP client and state machine."""
        self.client = httpx.AsyncClient(timeout=30.0)
        self.state_machine = WorkflowStateMachine()

    async def run_workflow(
        self,
        content_file: Path,
        output_format: str,
        layout_mode: str,
        progress: Progress | None = None,
        task: TaskID | None = None,
    ) -> dict[str, Any]:
        """
        Execute the complete document generation workflow.

        Returns:
            Result dictionary with status, session_id, proposal_id, and artifacts
        """
        try:
            # Load content
            with open(content_file) as f:
                content_data = json.load(f)

            # Step 1: Create intake session
            if progress and task:
                progress.update(task, description="Creating intake session...")
            session = await self._create_session(content_data)
            self.state_machine.transition(WorkflowState.SUBMITTED)

            # Step 2: Submit for layout generation
            if progress and task:
                progress.update(task, description="Submitting for layout generation...")
            await self._submit_session(session["session_id"], layout_mode)
            self.state_machine.transition(WorkflowState.LAYOUT_QUEUED)

            # Step 3: Poll for layout completion
            if progress and task:
                progress.update(task, description="Generating layout specification...")
            proposal_id = await self._poll_session_ready(session["session_id"])
            self.state_machine.transition(WorkflowState.LAYOUT_COMPLETE)

            # Step 4: Get layout specification
            if progress and task:
                progress.update(task, description="Retrieving layout specification...")
            lsp = await self._get_layout_spec(proposal_id)

            # Step 5: Render documents
            artifacts = []
            if output_format in ["word", "both"]:
                if progress and task:
                    progress.update(task, description="Rendering Word document...")
                word_artifact = await self._render_document(lsp)
                artifacts.append({"type": "word", "artifact_id": word_artifact["artifact_id"]})

            if output_format in ["pptx", "both"]:
                if progress and task:
                    progress.update(task, description="Rendering PowerPoint presentation...")
                pptx_artifact = await self._render_presentation(lsp)
                artifacts.append({"type": "powerpoint", "artifact_id": pptx_artifact["artifact_id"]})

            self.state_machine.transition(WorkflowState.DELIVERED)

            return {
                "status": "success",
                "session_id": session["session_id"],
                "proposal_id": proposal_id,
                "artifacts": artifacts,
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def get_session_status(self, session_id: str) -> dict[str, Any]:
        """Get the status of a session."""
        url = f"{settings.CONTENT_INTAKE_URL}/intake/sessions/{session_id}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def _create_session(self, content_data: dict[str, Any]) -> dict[str, Any]:
        """Create intake session."""
        url = f"{settings.CONTENT_INTAKE_URL}/intake/sessions"
        response = await self.client.post(url, json=content_data)
        response.raise_for_status()
        return response.json()

    async def _submit_session(self, session_id: str, layout_mode: str) -> dict[str, Any]:
        """Submit session for layout generation."""
        url = f"{settings.CONTENT_INTAKE_URL}/intake/sessions/{session_id}/submit"
        response = await self.client.post(url, json={"layout_mode": layout_mode})
        response.raise_for_status()
        return response.json()

    async def _poll_session_ready(
        self, session_id: str, max_attempts: int = 30, interval: float = 2.0
    ) -> str:
        """Poll session until layout is ready."""
        url = f"{settings.CONTENT_INTAKE_URL}/intake/sessions/{session_id}"

        for _ in range(max_attempts):
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "layout_complete":
                return data["proposal_id"]
            elif data["status"] == "failed":
                raise RuntimeError(f"Session failed: {data.get('error_message')}")

            await asyncio.sleep(interval)

        raise TimeoutError("Layout generation timed out")

    async def _get_layout_spec(self, proposal_id: str) -> dict[str, Any]:
        """Get layout specification."""
        url = f"{settings.GESTALT_ENGINE_URL}/layout/proposals/{proposal_id}/spec"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def _render_document(self, lsp: dict[str, Any]) -> dict[str, Any]:
        """Render Word document."""
        url = f"{settings.DOCUMENT_FORMATTER_URL}/render/documents"
        response = await self.client.post(url, json={"layout_specification": lsp})
        response.raise_for_status()
        return response.json()

    async def _render_presentation(self, lsp: dict[str, Any]) -> dict[str, Any]:
        """Render PowerPoint presentation."""
        url = f"{settings.DOCUMENT_FORMATTER_URL}/render/presentations"
        response = await self.client.post(url, json={"layout_specification": lsp})
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
