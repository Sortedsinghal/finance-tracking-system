"""FastAPI app entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base
from app.routers import auth, users, transactions, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Finance tracking API with RBAC and analytics.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(analytics.router)

static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/api/health", tags=["System"], summary="Health check")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_login_page():
    login_path = static_dir / "login.html"
    if login_path.exists():
        return HTMLResponse(content=login_path.read_text(), status_code=200)
    return HTMLResponse(content="<h1>Finance Tracker</h1><p>Visit <a href='/docs'>/docs</a> for API documentation.</p>")


@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def serve_dashboard():
    dashboard_path = static_dir / "index.html"
    if dashboard_path.exists():
        return HTMLResponse(content=dashboard_path.read_text(), status_code=200)
    return HTMLResponse(content="<h1>Dashboard</h1><p>Frontend not built yet.</p>")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred. Please try again later.",
            "error": str(exc) if settings.DEBUG else "Internal server error",
        },
    )
