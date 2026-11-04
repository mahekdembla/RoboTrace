"""RoboTrace 3D database package.

Provides ORM models and database session management.

Usage::

    from database.db import init_db, get_db, get_db_session
    from database.models import Mission, Agent, Task
"""

from database.db import close_db, get_db, get_db_session, init_db
from database.models import (
    Agent,
    Annotation,
    Base,
    Error,
    Evaluation,
    Mission,
    Task,
    TrajectoryEvent,
)

__all__ = [
    # Session management
    "init_db",
    "close_db",
    "get_db",
    "get_db_session",
    # Models
    "Base",
    "Mission",
    "Agent",
    "Task",
    "TrajectoryEvent",
    "Error",
    "Annotation",
    "Evaluation",
]

