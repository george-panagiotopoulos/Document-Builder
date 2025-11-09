"""
Proposal service business logic.

Handles proposal creation, layout generation, and specification retrieval.
"""

from typing import Any

from services.gestalt_engine.engines.design_engine import DesignEngine
from services.gestalt_engine.models.proposal import (
    DocumentType,
    LayoutSpecificationPackage,
    ProposalStatus,
)


class ProposalService:
    """Service for managing layout proposals."""

    def __init__(self) -> None:
        """Initialize proposal service."""
        self._proposals: dict[str, dict[str, Any]] = {}
        self._specifications: dict[str, LayoutSpecificationPackage] = {}
        self._idempotency_keys: dict[str, str] = {}
        self._design_engine = DesignEngine()

    async def create_proposal(
        self, cip: dict[str, Any], idempotency_key: str | None = None
    ) -> dict[str, Any]:
        """
        Create a new layout proposal from a Content-Intent Package.

        Validates the CIP and initiates layout generation.
        """
        # Check idempotency
        if idempotency_key and idempotency_key in self._idempotency_keys:
            proposal_id = self._idempotency_keys[idempotency_key]
            return self._proposals[proposal_id]

        # Validate CIP schema
        if "schema_version" not in cip or "session_id" not in cip:
            raise ValueError("Invalid CIP: missing required fields")

        # Generate proposal ID
        proposal_id = f"lsp-{cip['session_id'].split('-')[1]}"

        # Create proposal
        proposal = {
            "proposal_id": proposal_id,
            "status": ProposalStatus.QUEUED,
            "estimated_completion_seconds": 4,
            "session_id": cip["session_id"],
        }

        self._proposals[proposal_id] = proposal

        # Store idempotency key
        if idempotency_key:
            self._idempotency_keys[idempotency_key] = proposal_id

        # Generate layout specification asynchronously
        # In real implementation, this would be queued for async processing
        await self._generate_layout(proposal_id, cip)

        return proposal

    async def get_proposal(self, proposal_id: str) -> dict[str, Any] | None:
        """Retrieve proposal by ID."""
        return self._proposals.get(proposal_id)

    async def get_specification(self, proposal_id: str) -> LayoutSpecificationPackage | None:
        """Retrieve layout specification by proposal ID."""
        return self._specifications.get(proposal_id)

    async def _generate_layout(self, proposal_id: str, cip: dict[str, Any]) -> None:
        """
        Generate layout specification from CIP.

        Uses rule-based design engine to create LSP.
        """
        try:
            # Update proposal status
            self._proposals[proposal_id]["status"] = ProposalStatus.PROCESSING

            # Determine document type from design intent
            purpose = cip.get("design_intent", {}).get("purpose", "report")
            document_type = DocumentType.POWERPOINT if purpose == "presentation" else DocumentType.WORD

            # Generate layout using design engine
            lsp = self._design_engine.generate_layout(
                cip=cip,
                document_type=document_type,
                mode="rule_only",  # AI/LLM disabled per requirements
            )

            # Store specification
            self._specifications[proposal_id] = lsp

            # Update proposal status
            self._proposals[proposal_id]["status"] = ProposalStatus.COMPLETE

        except Exception as e:
            self._proposals[proposal_id]["status"] = ProposalStatus.FAILED
            self._proposals[proposal_id]["error"] = str(e)
