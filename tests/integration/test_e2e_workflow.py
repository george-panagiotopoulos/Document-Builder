"""
End-to-end integration test for Document Builder platform.

Tests the complete workflow:
1. Content Intake: Create session with sample content
2. Submit session for layout generation
3. Gestalt Engine: Generate layout specification
4. Document Formatter: Render Word and PowerPoint documents
"""

import pytest
import httpx
import asyncio
from pathlib import Path

# Service URLs (from environment or defaults)
CONTENT_INTAKE_URL = "http://localhost:8001/v1/intake"
GESTALT_ENGINE_URL = "http://localhost:8002/v1/layout"
DOCUMENT_FORMATTER_URL = "http://localhost:8003/v1/render"

# Sample content
SAMPLE_REQUEST = {
    "content_blocks": [
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
            "text": "Our team achieved remarkable growth this quarter with revenue increasing by 45% year-over-year.",
            "language": "en",
        },
    ],
    "images": [
        {
            "image_id": "img-001",
            "uri": "https://via.placeholder.com/800x600",
            "format": "png",
            "width_px": 800,
            "height_px": 600,
            "alt_text": "Revenue growth chart",
        },
        {
            "image_id": "img-002",
            "uri": "https://via.placeholder.com/800x600",
            "format": "png",
            "width_px": 800,
            "height_px": 600,
            "alt_text": "Market expansion map",
        },
    ],
    "design_intent": {
        "purpose": "presentation",
        "audience": "executive",
        "tone": "formal",
        "goals": ["clarity", "impact"],
    },
    "constraints": {
        "visual_density": "balanced",
        "max_pages": 10,
    },
}


@pytest.mark.asyncio
async def test_end_to_end_workflow():
    """
    Test complete end-to-end workflow from content intake to document generation.

    This test requires all three services to be running:
    - Content Intake Service on port 8001
    - Gestalt Design Engine on port 8002
    - Document Formatter Service on port 8003
    """

    async with httpx.AsyncClient(timeout=30.0) as client:
        # ===================================================================
        # Step 1: Create session in Content Intake
        # ===================================================================
        print("\n" + "="*70)
        print("STEP 1: Creating session in Content Intake Service")
        print("="*70)

        response = await client.post(
            f"{CONTENT_INTAKE_URL}/sessions",
            json=SAMPLE_REQUEST,
        )

        assert response.status_code == 201, f"Failed to create session: {response.text}"
        session_data = response.json()
        session_id = session_data["session_id"]

        print(f"✓ Session created: {session_id}")
        print(f"  Status: {session_data['status']}")

        # ===================================================================
        # Step 2: Submit session for layout generation
        # ===================================================================
        print("\n" + "="*70)
        print("STEP 2: Submitting session for layout generation")
        print("="*70)

        response = await client.post(
            f"{CONTENT_INTAKE_URL}/sessions/{session_id}/submit",
            json={"layout_mode": "rule_only"},
        )

        assert response.status_code == 200, f"Failed to submit session: {response.text}"
        submit_data = response.json()
        proposal_id = submit_data["proposal_id"]

        print(f"✓ Session submitted: {session_id}")
        print(f"  Proposal ID: {proposal_id}")
        print(f"  Status: {submit_data['status']}")

        # ===================================================================
        # Step 3: Poll Gestalt Engine for completion
        # ===================================================================
        print("\n" + "="*70)
        print("STEP 3: Polling Gestalt Engine for layout completion")
        print("="*70)

        max_attempts = 10
        for attempt in range(max_attempts):
            # Check status via Content Intake
            response = await client.post(
                f"{CONTENT_INTAKE_URL}/sessions/{session_id}/check-status"
            )

            assert response.status_code == 200, f"Failed to check status: {response.text}"
            status_data = response.json()

            print(f"  Attempt {attempt + 1}/{max_attempts}: Status = {status_data['status']}")

            if status_data["status"] == "layout_complete":
                print("✓ Layout generation complete!")
                break
            elif status_data["status"] == "failed":
                pytest.fail(f"Layout generation failed: {status_data.get('error_message')}")

            await asyncio.sleep(0.5)
        else:
            pytest.fail("Layout generation timed out")

        # ===================================================================
        # Step 4: Retrieve Layout Specification Package (LSP)
        # ===================================================================
        print("\n" + "="*70)
        print("STEP 4: Retrieving Layout Specification Package")
        print("="*70)

        response = await client.get(
            f"{GESTALT_ENGINE_URL}/proposals/{proposal_id}/spec"
        )

        assert response.status_code == 200, f"Failed to get LSP: {response.text}"
        lsp = response.json()

        print(f"✓ LSP retrieved for proposal: {proposal_id}")
        print(f"  Document type: {lsp['document_type']}")
        print(f"  Structure units: {len(lsp['structure'])}")
        print(f"  Quality grade: {lsp['design_rationale']['quality_grade']}")

        # ===================================================================
        # Step 5: Generate PowerPoint presentation
        # ===================================================================
        print("\n" + "="*70)
        print("STEP 5: Generating PowerPoint presentation")
        print("="*70)

        response = await client.post(
            f"{DOCUMENT_FORMATTER_URL}/presentations",
            json={"layout_specification": lsp},
        )

        assert response.status_code == 202, f"Failed to create presentation: {response.text}"
        pptx_job = response.json()

        print(f"✓ PowerPoint render job created: {pptx_job['render_job_id']}")
        print(f"  Status: {pptx_job['status']}")
        print(f"  Artifact ID: {pptx_job.get('artifact_id', 'pending')}")

        # Wait for rendering to complete
        render_job_id = pptx_job["render_job_id"]
        for attempt in range(10):
            response = await client.get(
                f"{DOCUMENT_FORMATTER_URL}/jobs/{render_job_id}"
            )
            job_status = response.json()

            if job_status["status"] == "complete":
                print(f"✓ PowerPoint rendering complete!")
                print(f"  Artifact: {job_status['artifact_id']}")
                break
            elif job_status["status"] == "failed":
                pytest.fail(f"Rendering failed: {job_status.get('error')}")

            await asyncio.sleep(0.3)

        # ===================================================================
        # Step 6: Generate Word document (change to word type)
        # ===================================================================
        print("\n" + "="*70)
        print("STEP 6: Generating Word document")
        print("="*70)

        # Modify LSP to Word type
        lsp_word = lsp.copy()
        lsp_word["document_type"] = "word"

        response = await client.post(
            f"{DOCUMENT_FORMATTER_URL}/documents",
            json={"layout_specification": lsp_word},
        )

        assert response.status_code == 202, f"Failed to create document: {response.text}"
        word_job = response.json()

        print(f"✓ Word render job created: {word_job['render_job_id']}")
        print(f"  Status: {word_job['status']}")
        print(f"  Artifact ID: {word_job.get('artifact_id', 'pending')}")

        # Wait for rendering to complete
        render_job_id = word_job["render_job_id"]
        for attempt in range(10):
            response = await client.get(
                f"{DOCUMENT_FORMATTER_URL}/jobs/{render_job_id}"
            )
            job_status = response.json()

            if job_status["status"] == "complete":
                print(f"✓ Word rendering complete!")
                print(f"  Artifact: {job_status['artifact_id']}")
                break
            elif job_status["status"] == "failed":
                pytest.fail(f"Rendering failed: {job_status.get('error')}")

            await asyncio.sleep(0.3)

        # ===================================================================
        # Verification
        # ===================================================================
        print("\n" + "="*70)
        print("END-TO-END TEST SUCCESSFUL")
        print("="*70)
        print("\nGenerated artifacts:")
        print(f"  - PowerPoint: {pptx_job.get('artifact_id')}.pptx")
        print(f"  - Word: {word_job.get('artifact_id')}.docx")
        print(f"\nWorkflow verified:")
        print("  ✓ Session creation")
        print("  ✓ Layout generation")
        print("  ✓ LSP retrieval")
        print("  ✓ Document formatting (Word & PowerPoint)")
        print("")

        # Check that files were created
        artifacts_dir = Path("artifacts")
        if artifacts_dir.exists():
            pptx_file = artifacts_dir / f"{pptx_job.get('artifact_id')}.pptx"
            word_file = artifacts_dir / f"{word_job.get('artifact_id')}.docx"

            assert pptx_file.exists(), f"PowerPoint file not found: {pptx_file}"
            assert word_file.exists(), f"Word file not found: {word_file}"

            print(f"✓ Verified file existence:")
            print(f"  - {pptx_file} ({pptx_file.stat().st_size} bytes)")
            print(f"  - {word_file} ({word_file.stat().st_size} bytes)")


if __name__ == "__main__":
    # Run test directly
    asyncio.run(test_end_to_end_workflow())
