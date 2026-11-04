"""Backward-compatible re-exports from the database package.

All database functionality now lives in :mod:`database.db` and
:mod:`database.models`.  This module re-exports the most common symbols
so that existing ``from app.database import …`` imports continue to work.
"""

from database.db import (  # noqa: F401
    AsyncSessionLocal,
    close_db,
    engine,
    get_db,
    get_db_session,
    init_db,
)
from database.models import Base  # noqa: F401
