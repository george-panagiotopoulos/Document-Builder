"""
API endpoints for layout proposal management.

Provides REST endpoints for creating and retrieving layout proposals.
"""

from fastapi import APIRouter, HTTPException, Header, status
from typing import Annotated, Any

from services.gestalt_engine.models.proposal import (
    LayoutSpecificationPackage,
    ProposalResponse,
)
from services.gestalt_engine.services.proposal_service import ProposalService

router = APIRouter()
proposal_service = ProposalService()


@router.post("/proposals", response_model=ProposalResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_proposal(
    cip: dict[str, Any],
    idempotency_key: Annotated[str | None, Header()] = None,
) -> ProposalResponse:
    """
    Submit a Content-Intent Package (CIP) to generate layout proposals.

    Returns proposal_id for polling status.
    """
    try:
        proposal = await proposal_service.create_proposal(cip, idempotency_key)
        return ProposalResponse(
            proposal_id=proposal["proposal_id"],
            status=proposal["status"],
            estimated_completion_seconds=proposal.get("estimated_completion_seconds"),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/proposals/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(proposal_id: str) -> ProposalResponse:
    """
    Retrieve proposal status and metadata.

    Returns current processing state and error information if failed.
    """
    proposal = await proposal_service.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")

    return ProposalResponse(
        proposal_id=proposal["proposal_id"],
        status=proposal["status"],
        error=proposal.get("error"),
    )


@router.get("/proposals/{proposal_id}/spec", response_model=LayoutSpecificationPackage)
async def get_specification(proposal_id: str) -> LayoutSpecificationPackage:
    """
    Download the finalized Layout Specification Package (LSP) JSON.

    Returns the complete LSP with design rationale.
    """
    lsp = await proposal_service.get_specification(proposal_id)
    if not lsp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specification not found")

    return lsp
