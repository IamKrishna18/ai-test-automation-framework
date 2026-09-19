"""Database engine and session management.

Uses SQLAlchemy 2.0 with async-compatible patterns.
The connection URL comes from Settings, defaulting to SQLite.
Switching to PostgreSQL requires only changing DATABASE_URL.

Usage:
    from app.core.database import get_db, Base

    # In FastAPI route:
    @router.get("/items")
    def list_items(db: Session = Depends(get_db)):
        ...
"""

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def _get_engine():
    """Create the SQLAlchemy engine from settings."""
    settings = get_settings()
    connect_args = {}

    # SQLite-specific: enable WAL mode and foreign keys
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(
        settings.database_url,
        connect_args=connect_args,
        echo=False,
    )

    # Enable foreign key enforcement for SQLite
    if settings.database_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine = _get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables defined by ORM models.

    Called once at application startup. In production, this would be
    replaced by Alembic migrations.
    """
    # Import models so they register with Base.metadata
    import app.models  # noqa: F401

    settings = get_settings()
    settings.data_dir  # Ensure data directory exists

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session.

    The session is automatically closed when the request completes,
    whether or not an exception occurred.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
