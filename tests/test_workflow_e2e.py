#!/usr/bin/env python3
"""
Test script for end-to-end document generation workflow.

Tests the complete workflow:
1. Create session with content
2. Submit for layout generation
3. Poll until layout complete
4. Get layout specification
5. Render DOCX and PPTX documents
6. Download generated files
"""

import asyncio
import json
import httpx
from pathlib import Path

# Service URLs
CONTENT_INTAKE_URL = "http://localhost:8001/v1/intake"
GESTALT_ENGINE_URL = "http://localhost:8002/v1/layout"
DOCUMENT_FORMATTER_URL = "http://localhost:8003/v1/render"

# Test content
TEST_TEXT = """Temenos Transact operates on a robust n-tier architecture that distinctly separates its core layers: database, business logic, APIs, and user interface. This separation enhances modularity, scalability, and manageability, ensuring the system can efficiently handle complex banking operations.

At the foundation, the database serves purely as a data repository without embedded business logic or stored procedures. It supports strong consistency, allowing multiple concurrent transactions while ensuring all users access the same accurate data simultaneously. This design promotes scalability and simplifies maintenance, with the underlying database engine managing scaling and automatic failover to maintain uptime.

The business logic layer is implemented primarily in Java, with legacy code compiled into Java bytecode via the Temenos Application Framework for Java (TAFJ). This layer encompasses the core banking functionality, including modules like Arrangement Architecture for product engines, Customer, Limits, Payments, and General Ledger. The logic is parameter-driven, enabling extensive configuration without code changes, and incorporates validation checks to ensure transaction integrity.

Communication with the core logic occurs through a proprietary messaging protocol called OFS (Open Financial Service), which can be accessed either via the Temenos Open Connectivity Framework (TOCF) using JMS/MQ queues for resilience or directly through Enterprise Java Beans (EJB) for lower latency.

APIs are provided as RESTful services using JSON payloads, adhering to semantic versioning and documented with OpenAPI specifications. These APIs facilitate synchronous interactions and support extensibility through the Extensibility Framework and Java APIs. Event-based integration is also supported via business and data events, leveraging pub/sub systems like Kafka, Azure Event Hubs, or AWS Kinesis.

The user interface consists of two main types: the auto-generated Transact Explorer for rapid back-office productivity and hand-crafted user agents built with Unified UX (UUX) for ergonomic, role-specific dashboards. Both interfaces are unified under Temenos Explorer, providing single sign-on and consistent look and feel.

Overall, this layered architecture ensures that data storage, business logic, integration, and user interaction are cleanly separated, promoting flexibility, scalability, and ease of customization.

The main business benefit of this architecture is its ability to provide banks with a highly scalable, flexible, and reliable core banking system that can be tailored to diverse operational needs while ensuring consistent data integrity and seamless integration across multiple channels. This empowers banks to innovate rapidly and deliver superior customer experiences."""


async def test_workflow():
    """Run end-to-end workflow test."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        print("=" * 80)
        print("End-to-End Document Generation Workflow Test")
        print("=" * 80)
        print()

        # Step 1: Create session
        print("Step 1: Creating intake session...")
        session_payload = {
            "content_blocks": [
                {
                    "type": "paragraph",
                    "level": 0,
                    "sequence": 0,
                    "text": TEST_TEXT,
                    "language": "en"
                }
            ],
            "images": [],
            "design_intent": {
                "purpose": "report",
                "audience": "technical",
                "tone": "formal",
                "goals": ["clarity"],
                "primary_actions": [],
                "success_metrics": []
            },
            "constraints": {
                "visual_density": "balanced",
                "color_policy": {},
                "brand_guidelines": {},
                "document_preferences": {},
                "presentation_preferences": {}
            }
        }

        response = await client.post(
            f"{CONTENT_INTAKE_URL}/sessions",
            json=session_payload
        )
        response.raise_for_status()
        session = response.json()
        session_id = session["session_id"]
        print(f"✓ Session created: {session_id}")
        print(f"  Status: {session['status']}")
        print()

        # Step 2: Submit for layout generation
        print("Step 2: Submitting session for layout generation...")
        response = await client.post(
            f"{CONTENT_INTAKE_URL}/sessions/{session_id}/submit",
            json={"layout_mode": "rule_only"}
        )
        response.raise_for_status()
        session = response.json()
        proposal_id = session.get("proposal_id")
        print(f"✓ Session submitted")
        print(f"  Status: {session['status']}")
        print(f"  Proposal ID: {proposal_id}")
        print()

        # Step 3: Poll until layout complete
        print("Step 3: Polling for layout completion...")
        max_attempts = 30
        for attempt in range(max_attempts):
            response = await client.post(
                f"{CONTENT_INTAKE_URL}/sessions/{session_id}/check-status"
            )
            response.raise_for_status()
            session = response.json()
            status = session["status"]

            if status == "layout_complete":
                print(f"✓ Layout generation complete!")
                proposal_id = session.get("proposal_id")
                break
            elif status == "failed":
                raise RuntimeError(f"Layout generation failed: {session.get('error_message')}")

            await asyncio.sleep(2)
            print(f"  Attempt {attempt + 1}/{max_attempts}: Status = {status}")

        if status != "layout_complete":
            raise TimeoutError("Layout generation timed out")
        print()

        # Step 4: Get layout specification
        print("Step 4: Retrieving layout specification...")
        response = await client.get(
            f"{GESTALT_ENGINE_URL}/proposals/{proposal_id}/spec"
        )
        response.raise_for_status()
        lsp = response.json()
        print(f"✓ Layout specification retrieved")
        print(f"  Document type: {lsp.get('document_type')}")
        print(f"  Structure units: {len(lsp.get('structure', []))}")
        print()

        # Step 5: Render Word document
        print("Step 5: Rendering Word document (DOCX)...")
        response = await client.post(
            f"{DOCUMENT_FORMATTER_URL}/documents",
            json={"layout_specification": lsp}
        )
        response.raise_for_status()
        word_job = response.json()
        word_artifact_id = word_job.get("artifact_id")
        print(f"✓ Word document rendered")
        print(f"  Job ID: {word_job.get('render_job_id')}")
        print(f"  Artifact ID: {word_artifact_id}")
        print()

        # Step 6: Render PowerPoint presentation
        print("Step 6: Rendering PowerPoint presentation (PPTX)...")
        # Update LSP for PowerPoint
        lsp_pptx = lsp.copy()
        lsp_pptx["document_type"] = "powerpoint"
        response = await client.post(
            f"{DOCUMENT_FORMATTER_URL}/presentations",
            json={"layout_specification": lsp_pptx}
        )
        response.raise_for_status()
        pptx_job = response.json()
        pptx_artifact_id = pptx_job.get("artifact_id")
        print(f"✓ PowerPoint presentation rendered")
        print(f"  Job ID: {pptx_job.get('render_job_id')}")
        print(f"  Artifact ID: {pptx_artifact_id}")
        print()

        # Step 7: Check artifact locations
        print("Step 7: Checking generated artifacts...")
        artifacts_dir = Path("infrastructure/data/artifacts")
        word_file = artifacts_dir / f"{word_artifact_id}.docx"
        pptx_file = artifacts_dir / f"{pptx_artifact_id}.pptx"

        if word_file.exists():
            print(f"✓ Word document found: {word_file} ({word_file.stat().st_size} bytes)")
        else:
            print(f"✗ Word document not found: {word_file}")

        if pptx_file.exists():
            print(f"✓ PowerPoint presentation found: {pptx_file} ({pptx_file.stat().st_size} bytes)")
        else:
            print(f"✗ PowerPoint presentation not found: {pptx_file}")

        print()
        print("=" * 80)
        print("Workflow Test Complete!")
        print("=" * 80)
        print(f"Session ID: {session_id}")
        print(f"Proposal ID: {proposal_id}")
        print(f"Word Document: {word_file if word_file.exists() else 'Not found'}")
        print(f"PowerPoint Presentation: {pptx_file if pptx_file.exists() else 'Not found'}")


if __name__ == "__main__":
    asyncio.run(test_workflow())

