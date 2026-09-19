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

    @app.get("/health", tags=["health"])
    def health_check():
        """Simple health check endpoint."""
        return {"status": "healthy", "version": "0.1.0"}

    return app


app = create_app()
