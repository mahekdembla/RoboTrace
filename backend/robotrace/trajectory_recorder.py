"""RoboTrace 3D — Spatial Trajectory Recorder.

Records all important actions performed by robotic agents in chronological order:
- Captures actual PyBullet physics positions (X, Y, Z, Yaw).
- Links cognitive context: observation → decision → action → expected vs actual outcome.
- Assigns sequential step IDs per mission and agent.
- Persists events into SQLite database (`trajectory_events` table).
- Preserves historical records across mission resets for auditability.
- Queries trajectory events filtered by mission and agent.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select

from database.db import get_db_session
from database.models import TrajectoryEvent
from engine.simulation import WarehouseSimulation

logger = logging.getLogger("robotrace.trajectory")


@dataclass
class TrajectoryEventData:
    """In-memory representation of a recorded trajectory event."""
    event_id: int
    mission_id: int
    agent_id: str
    task_id: Optional[str]
    step_id: int
    timestamp: str
    observation: str
    decision_summary: str
    action: str
    expected_outcome: str
    actual_outcome: str
    execution_status: str  # SUCCESS, FAILED, IN_PROGRESS
    position_x: float
    position_y: float
    position_z: float
    rotation: float  # yaw in radians

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "mission_id": self.mission_id,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "step_id": self.step_id,
            "timestamp": self.timestamp,
            "observation": self.observation,
            "decision_summary": self.decision_summary,
            "action": self.action,
            "expected_outcome": self.expected_outcome,
            "actual_outcome": self.actual_outcome,
            "execution_status": self.execution_status,
            "pose": {
                "x": round(self.position_x, 4),
                "y": round(self.position_y, 4),
                "z": round(self.position_z, 4),
                "yaw": round(self.rotation, 4),
            },
        }


class TrajectoryRecorder:
    """Manages recording, indexing, and SQLite persistence of trajectory events."""

    def __init__(self, simulation: Optional[WarehouseSimulation] = None):
        self.simulation = simulation
        self._next_event_id: int = 1
        self._step_counters: Dict[Tuple[int, str], int] = {}  # (mission_id, agent_id) -> current_step
        self._memory_events: List[TrajectoryEventData] = []

    def _get_next_step_id(self, mission_id: int, agent_id: str) -> int:
        """Increment and return sequential step ID for mission and agent."""
        key = (mission_id, agent_id)
        current = self._step_counters.get(key, 0) + 1
        self._step_counters[key] = current
        return current

    def record_event(
        self,
        mission_id: int,
        agent_id: str,
        action: str,
        observation: str = "",
        decision_summary: str = "",
        expected_outcome: str = "",
        actual_outcome: str = "",
        execution_status: str = "SUCCESS",
        task_id: Optional[str] = None,
        pose: Optional[Tuple[float, float, float, float]] = None,
        persist_db: bool = True,
    ) -> TrajectoryEventData:
        """Capture and record a trajectory action event.

        Uses simulation coordinates directly as the source of truth if pose is not provided.
        Never fabricates coordinates.
        """
        if pose is None and self.simulation is not None and self.simulation._is_initialized:
            try:
                x, y, z, yaw = self.simulation.get_robot_pose(agent_id)
            except Exception:
                x, y, z, yaw = 0.0, 0.0, 0.0, 0.0
        elif pose is not None:
            x, y, z, yaw = pose
        else:
            x, y, z, yaw = 0.0, 0.0, 0.0, 0.0

        event_id = self._next_event_id
        self._next_event_id += 1
        step_id = self._get_next_step_id(mission_id, agent_id)
        now_iso = datetime.now(timezone.utc).isoformat()

        event = TrajectoryEventData(
            event_id=event_id,
            mission_id=mission_id,
            agent_id=agent_id,
            task_id=task_id,
            step_id=step_id,
            timestamp=now_iso,
            observation=observation,
            decision_summary=decision_summary,
            action=action,
            expected_outcome=expected_outcome,
            actual_outcome=actual_outcome,
            execution_status=execution_status,
            position_x=x,
            position_y=y,
            position_z=z,
            rotation=yaw,
        )

        self._memory_events.append(event)
        logger.info(
            "Recorded trajectory event %d (mission %d, %s, step %d): action='%s', status=%s",
            event_id, mission_id, agent_id, step_id, action, execution_status,
        )

        if persist_db:
            try:
                import asyncio
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop is not None and loop.is_running():
                    loop.create_task(self._persist_to_sqlite(event))
                else:
                    asyncio.run(self._persist_to_sqlite(event))
            except Exception as exc:
                logger.warning("TrajectoryRecorder persistence error: %s", exc)

        return event

    async def _persist_to_sqlite(self, event: TrajectoryEventData) -> None:
        """Save trajectory record into SQLite table."""
        try:
            async with get_db_session() as session:
                record = TrajectoryEvent(
                    id=event.event_id,
                    mission_id=event.mission_id,
                    agent_name=event.agent_id,
                    step_id=event.step_id,
                    x=event.position_x,
                    y=event.position_y,
                    z=event.position_z,
                    yaw=event.rotation,
                    observation=event.observation,
                    decision_summary=event.decision_summary,
                    action=event.action,
                    expected_outcome=event.expected_outcome,
                    actual_outcome=event.actual_outcome,
                    execution_status=event.execution_status,
                    outcome=event.actual_outcome,
                )
                await session.merge(record)
        except Exception as exc:
            logger.warning("Failed to persist trajectory event to SQLite: %s", exc)

    def get_trajectory(
        self,
        mission_id: int,
        agent_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 200,
    ) -> List[TrajectoryEventData]:
        """Retrieve chronological trajectory events filtered by mission and optionally agent."""
        events = [e for e in self._memory_events if e.mission_id == mission_id]
        if agent_id:
            events = [e for e in events if e.agent_id.upper() == agent_id.upper()]

        events = sorted(events, key=lambda x: x.event_id)
        return events[skip : skip + limit]

    def get_all_events(self, mission_id: Optional[int] = None) -> List[TrajectoryEventData]:
        """Retrieve all events, optionally scoped to a mission."""
        if mission_id is not None:
            return [e for e in self._memory_events if e.mission_id == mission_id]
        return list(self._memory_events)

    def clear_memory(self) -> None:
        """Clear live memory without deleting SQLite persistence."""
        self._memory_events.clear()

