"""
User Agent Orchestrator main entry point.

This CLI orchestrates the end-to-end document generation workflow by
coordinating REST API calls across all services.
"""

import asyncio
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from services.user_agent.workflow.orchestrator import WorkflowOrchestrator
from services.user_agent.utils.config import settings

app = typer.Typer(help="Document Builder User Agent - Orchestrate document generation workflows")
console = Console()


@app.command()
def generate(
    content_file: Path = typer.Argument(..., help="Path to content JSON file"),
    output_format: str = typer.Option("both", "--format", "-f", help="Output format: word, pptx, or both"),
    layout_mode: str = typer.Option("rule_only", "--mode", "-m", help="Layout mode: rule_only, ai_assist, or ai_full"),
) -> None:
    """
    Generate documents from content file.

    Orchestrates the full workflow: content intake → layout generation → rendering.
    """
    if not content_file.exists():
        console.print(f"[red]Error: Content file not found: {content_file}[/red]")
        raise typer.Exit(1)

    console.print(f"[bold blue]Document Builder User Agent[/bold blue]")
    console.print(f"Content file: {content_file}")
    console.print(f"Output format: {output_format}")
    console.print(f"Layout mode: {layout_mode}")
    console.print()

    orchestrator = WorkflowOrchestrator()

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing workflow...", total=None)

            # Run async workflow
            result = asyncio.run(
                orchestrator.run_workflow(
                    content_file=content_file,
                    output_format=output_format,
                    layout_mode=layout_mode,
                    progress=progress,
                    task=task,
                )
            )

        if result["status"] == "success":
            console.print(f"\n[bold green]✓ Workflow completed successfully![/bold green]")
            console.print(f"\nSession ID: {result['session_id']}")
            console.print(f"Proposal ID: {result['proposal_id']}")

            if "artifacts" in result:
                console.print("\nGenerated artifacts:")
                for artifact in result["artifacts"]:
                    console.print(f"  - {artifact['type']}: {artifact['artifact_id']}")
        else:
            console.print(f"\n[bold red]✗ Workflow failed: {result.get('error', 'Unknown error')}[/bold red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"\n[bold red]✗ Error: {str(e)}[/bold red]")
        raise typer.Exit(1)


@app.command()
def status(
    session_id: str = typer.Argument(..., help="Session ID to check"),
) -> None:
    """Check status of a document generation session."""
    console.print(f"[bold blue]Checking session status...[/bold blue]")
    console.print(f"Session ID: {session_id}")
    console.print()

    orchestrator = WorkflowOrchestrator()

    try:
        result = asyncio.run(orchestrator.get_session_status(session_id))
        console.print(f"Status: [bold]{result['status']}[/bold]")

        if "proposal_id" in result and result["proposal_id"]:
            console.print(f"Proposal ID: {result['proposal_id']}")

        if "error" in result and result["error"]:
            console.print(f"[red]Error: {result['error']}[/red]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"[bold]Document Builder User Agent[/bold]")
    console.print(f"Version: {settings.SERVICE_VERSION}")
    console.print(f"Services:")
    console.print(f"  - Content Intake: {settings.CONTENT_INTAKE_URL}")
    console.print(f"  - Gestalt Engine: {settings.GESTALT_ENGINE_URL}")
    console.print(f"  - Document Formatter: {settings.DOCUMENT_FORMATTER_URL}")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
