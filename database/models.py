"""SQLAlchemy ORM models for RoboTrace 3D.

Defines seven tables that capture the full lifecycle of a robotic mission:
missions, agents, tasks, trajectory_events, errors, annotations, and evaluations.

Design principles:
    - All timestamps are stored in UTC via ``datetime.now(timezone.utc)``.
    - Robot coordinates (x, y, z) and orientation (roll, pitch, yaw) are stored
      as Float columns for numerical precision.
    - The ``Error.suggested_category`` column holds the original AgentGuard
      prediction and is **never overwritten**. Human corrections live in a
      separate ``Annotation`` row linked by foreign key.
    - Cascade deletes propagate from parent to child so that removing a mission
      cleans up all dependent records.
"""

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utcnow() -> datetime:
    """Return the current UTC timestamp (timezone-aware)."""
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class MissionStatus(str, enum.Enum):
    """Allowed states for a mission."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentStatus(str, enum.Enum):
    """Allowed states for an agent."""
    IDLE = "IDLE"
    ASSIGNED = "ASSIGNED"
    MOVING = "MOVING"
    WORKING = "WORKING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"


class TaskStatus(str, enum.Enum):
    """Allowed states for a task."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ErrorSeverity(str, enum.Enum):
    """Severity levels for logged errors."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ReviewStatus(str, enum.Enum):
    """Review lifecycle statuses for annotations."""
    PENDING_REVIEW = "PENDING_REVIEW"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    CORRECTED = "CORRECTED"


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    """Declarative base class for all RoboTrace ORM models."""
    pass


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Mission(Base):
    """A high-level robotic mission container."""

    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=MissionStatus.PENDING.value,
    )
    environment: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, default="warehouse_floor_1",
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow,
    )

    # -- relationships -------------------------------------------------------
    agents: Mapped[list["Agent"]] = relationship(
        back_populates="mission", cascade="all, delete-orphan",
    )
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="mission", cascade="all, delete-orphan",
    )
    evaluations: Mapped[list["Evaluation"]] = relationship(
        back_populates="mission", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Mission(id={self.id}, name='{self.name}', status='{self.status}')>"


class Agent(Base):
    """A robotic agent assigned to a mission."""

    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("missions.id", ondelete="CASCADE"), nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    agent_type: Mapped[str] = mapped_column(
        String(100), nullable=False, doc="E.g. ATLAS, NOVA, TITAN",
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=AgentStatus.IDLE.value,
    )
    config_metadata: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, doc="JSON-encoded agent configuration",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow,
    )

    # -- relationships -------------------------------------------------------
    mission: Mapped["Mission"] = relationship(back_populates="agents")
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="agent", cascade="all, delete-orphan",
    )
    trajectory_events: Mapped[list["TrajectoryEvent"]] = relationship(
        back_populates="agent", cascade="all, delete-orphan",
    )
    errors: Mapped[list["Error"]] = relationship(
        back_populates="agent", cascade="all, delete-orphan",
    )
    evaluations: Mapped[list["Evaluation"]] = relationship(
        back_populates="agent", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.agent_type}')>"


class Task(Base):
    """An individual task assigned to an agent within a mission."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("missions.id", ondelete="CASCADE"), nullable=False,
    )
    agent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=TaskStatus.PENDING.value,
    )
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow,
    )

    # -- relationships -------------------------------------------------------
    mission: Mapped["Mission"] = relationship(back_populates="tasks")
    agent: Mapped["Agent"] = relationship(back_populates="tasks")
    trajectory_events: Mapped[list["TrajectoryEvent"]] = relationship(
        back_populates="task", cascade="all, delete-orphan",
    )
    errors: Mapped[list["Error"]] = relationship(
        back_populates="task", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, name='{self.name}', status='{self.status}')>"


class TrajectoryEvent(Base):
    """A timestamped position and context snapshot for an agent during a task."""

    __tablename__ = "trajectory_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True,
    )
    agent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=True,
    )
    mission_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    agent_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    step_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow,
    )

    # -- 3-D coordinates (numerical) -----------------------------------------
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    z: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # -- orientation (radians) ------------------------------------------------
    roll: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    pitch: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    yaw: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)

    # -- velocities -----------------------------------------------------------
    linear_velocity: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    angular_velocity: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)

    # -- cognitive context ----------------------------------------------------
    observation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decision_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actual_outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="SUCCESS")
    outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # -- relationships -------------------------------------------------------
    task: Mapped[Optional["Task"]] = relationship(back_populates="trajectory_events")
    agent: Mapped[Optional["Agent"]] = relationship(back_populates="trajectory_events")

    def __repr__(self) -> str:
        return (
            f"<TrajectoryEvent(id={self.id}, agent={self.agent_name or self.agent_id}, "
            f"pos=({self.x}, {self.y}, {self.z}))>"
        )


class Error(Base):
    """An error recorded during task execution.

    The ``suggested_category`` stores the **original AgentGuard prediction**
    and must never be overwritten.  Human corrections are stored in a separate
    :class:`Annotation` row linked via ``error_id``.
    """

    __tablename__ = "errors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True,
    )
    agent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=True,
    )
    mission_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    agent_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    step_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow,
    )

    error_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ErrorSeverity.MEDIUM.value,
    )

    # AgentGuard prediction — IMMUTABLE once written.
    suggested_category: Mapped[str] = mapped_column(
        String(255), nullable=False,
        doc="Original AgentGuard prediction. Never overwrite this value.",
    )

    rule_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # -- resolution -----------------------------------------------------------
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    review_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=ReviewStatus.PENDING_REVIEW.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow,
    )

    # -- relationships -------------------------------------------------------
    task: Mapped[Optional["Task"]] = relationship(back_populates="errors")
    agent: Mapped[Optional["Agent"]] = relationship(back_populates="errors")
    annotations: Mapped[list["Annotation"]] = relationship(
        back_populates="error", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Error(id={self.id}, severity='{self.severity}', "
            f"suggested='{self.suggested_category}')>"
        )


class Annotation(Base):
    """A human annotation / correction applied to an :class:`Error`."""

    __tablename__ = "annotations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    error_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("errors.id", ondelete="CASCADE"), nullable=False,
    )
    original_suggested_category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    corrected_category: Mapped[str] = mapped_column(String(255), nullable=False)
    review_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=ReviewStatus.CORRECTED.value,
    )
    annotator: Mapped[str] = mapped_column(
        String(255), nullable=False, doc="Identity of the human reviewer",
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow,
    )

    # -- relationships -------------------------------------------------------
    error: Mapped["Error"] = relationship(back_populates="annotations")

    def __repr__(self) -> str:
        return (
            f"<Annotation(id={self.id}, corrected='{self.corrected_category}', "
            f"by='{self.annotator}')>"
        )


class Evaluation(Base):
    """A performance evaluation for a mission or a specific agent."""

    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("missions.id", ondelete="CASCADE"), nullable=False,
    )
    agent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=True,
    )

    evaluator: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    metrics: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow,
    )

    # -- relationships -------------------------------------------------------
    mission: Mapped["Mission"] = relationship(back_populates="evaluations")
    agent: Mapped[Optional["Agent"]] = relationship(back_populates="evaluations")

    def __repr__(self) -> str:
        return (
            f"<Evaluation(id={self.id}, score={self.score}, "
            f"evaluator='{self.evaluator}')>"
        )
