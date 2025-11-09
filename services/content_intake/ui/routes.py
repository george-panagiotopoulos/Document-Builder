"""Web UI routes for Content Intake Service."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()

# Set up templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Render home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/sessions/new", response_class=HTMLResponse)
async def new_session(request: Request) -> HTMLResponse:
    """Render new session form."""
    return templates.TemplateResponse("new_session.html", {"request": request})


@router.get("/sessions/{session_id}", response_class=HTMLResponse)
async def view_session(request: Request, session_id: str) -> HTMLResponse:
    """Render session detail page."""
    return templates.TemplateResponse(
        "session_detail.html",
        {"request": request, "session_id": session_id}
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """Render dashboard."""
    return templates.TemplateResponse("dashboard.html", {"request": request})
