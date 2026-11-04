"""Database connection configuration and session management.

Provides:
    - An async SQLAlchemy engine connected to a local SQLite file.
    - A session factory for creating database sessions.
    - ``get_db()`` — a FastAPI dependency that yields a managed session.
    - ``get_db_session()`` — an async context manager for use outside FastAPI.
    - ``init_db()`` / ``close_db()`` — lifecycle helpers for startup/shutdown.

The SQLite database file (``robotrace.db`` by default) is stored in the
backend directory and excluded from Git via ``.gitignore``.
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from database.models import Base

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "robotrace.db"
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{DEFAULT_DB_PATH.as_posix()}",
)

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
)


# Enable SQLite foreign-key enforcement and concurrency optimizations.
@event.listens_for(engine.sync_engine, "connect")
def _enable_sqlite_fk(dbapi_connection, connection_record):
    """Turn on foreign keys, WAL mode, and busy timeout for SQLite connections."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA journal_mode = WAL")
    cursor.execute("PRAGMA busy_timeout = 30000")
    cursor.close()


# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Lifecycle helpers
# ---------------------------------------------------------------------------

async def init_db() -> None:
    """Create all tables defined in :mod:`database.models`.

    Safe to call multiple times — existing tables are left untouched.

    Raises:
        SQLAlchemyError: If the database cannot be reached or the schema
            cannot be applied.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully.")
    except SQLAlchemyError as exc:
        logger.error("Failed to initialise database: %s", exc)
        raise


async def close_db() -> None:
    """Dispose of the engine and release all pooled connections."""
    await engine.dispose()
    logger.info("Database engine disposed.")


# ---------------------------------------------------------------------------
# Session providers
# ---------------------------------------------------------------------------

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session.

    The session is **committed** when the request handler returns normally
    and **rolled back** on any exception.  It is always closed afterwards.

    Usage::

        @router.get("/missions")
        async def list_missions(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Mission))
            return result.scalars().all()
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except SQLAlchemyError as exc:
        await session.rollback()
        logger.error("Database session error (rolled back): %s", exc)
        raise
    finally:
        await session.close()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager for obtaining a session outside of FastAPI.

    Useful in CLI scripts, background workers, or tests::

        async with get_db_session() as session:
            mission = Mission(name="Recon Alpha")
            session.add(mission)
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except SQLAlchemyError as exc:
        await session.rollback()
        logger.error("Database session error (rolled back): %s", exc)
        raise
    finally:
        await session.close()
