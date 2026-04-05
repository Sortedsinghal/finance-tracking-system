"""
FastAPI application entry point.

Configures the app, registers routers, serves static files,
and creates database tables on startup.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base
from app.routers import auth, users, transactions, analytics


# ── Lifespan: create tables on startup ───────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all database tables when the app starts."""
    Base.metadata.create_all(bind=engine)
    yield


# ── App instance ─────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A Python-powered finance tracking system for managing financial records, "
        "generating analytics, and supporting role-based access control."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(analytics.router)


# ── Static files ─────────────────────────────────────────
static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ── Health check ─────────────────────────────────────────
@app.get("/api/health", tags=["System"], summary="Health check")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# ── Serve frontend pages ────────────────────────────────
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_login_page():
    """Serve the login page as the root."""
    login_path = static_dir / "login.html"
    if login_path.exists():
        return HTMLResponse(content=login_path.read_text(), status_code=200)
    return HTMLResponse(content="<h1>Finance Tracker</h1><p>Visit <a href='/docs'>/docs</a> for API documentation.</p>")


@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def serve_dashboard():
    """Serve the main dashboard page."""
    dashboard_path = static_dir / "index.html"
    if dashboard_path.exists():
        return HTMLResponse(content=dashboard_path.read_text(), status_code=200)
    return HTMLResponse(content="<h1>Dashboard</h1><p>Frontend not built yet.</p>")


# ── Global exception handler ────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return a clean JSON error."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred. Please try again later.",
            "error": str(exc) if settings.DEBUG else "Internal server error",
        },
    )
