"""FastAPI application entry point.

Sets up the application, includes routers, configures CORS,
and initializes the database on startup.

Usage:
    uvicorn app.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dashboard import router as dashboard_router
from app.api.reports import router as reports_router
from app.api.runs import router as runs_router
from app.core.config import get_settings
from app.core.database import init_db
from app.core.logging import get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager.

    Runs setup on startup and cleanup on shutdown.
    """
    # Startup
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Starting AI Test Automation Framework")

    init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down AI Test Automation Framework")


def create_app() -> FastAPI:
    """Application factory.

    Returns a configured FastAPI instance with all routers
    and middleware registered.
    """
    settings = get_settings()

    app = FastAPI(
        title="AI Test Automation Framework",
        description=(
            "AI-driven API test generation, validation, execution, "
            "and evaluation platform."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS - allow frontend origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            settings.frontend_url,
            "http://localhost:5173",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(runs_router)
    app.include_router(dashboard_router)
    app.include_router(reports_router)

    # Mount sample target API for unified demo and production deployments
    try:
        import os
        import sys
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)
        from sample_target_api.app import app as target_app
        app.mount("/sample-api", target_app)
    except Exception as e:
        logger.warning(f"Could not mount sample target API: {e}")

    @app.get("/health", tags=["health"])
    def health_check():
        """Simple health check endpoint."""
        return {"status": "healthy", "version": "0.1.0"}

    # Serve built frontend static files if present (for single-container/production deployments)
    frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
    if os.path.isdir(frontend_dist):
        from fastapi.staticfiles import StaticFiles
        from fastapi.responses import FileResponse

        assets_dir = os.path.join(frontend_dist, "assets")
        if os.path.isdir(assets_dir):
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str):
            file_path = os.path.join(frontend_dist, full_path)
            if full_path and os.path.isfile(file_path):
                return FileResponse(file_path)
            return FileResponse(os.path.join(frontend_dist, "index.html"))

    return app


app = create_app()
