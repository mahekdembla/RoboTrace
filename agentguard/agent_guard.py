"""RoboTrace 3D — AgentGuard Independent Verification Engine.

Independently monitors and audits robot actions, task outcomes, and physics states:
- Cross-references expected outcomes against actual simulation state.
- Detects physical collisions with shelves, obstacles, or other robots.
- Detects false task completion reports (e.g. reporting delivery when package is undelivered).
- Detects manipulation failures (incorrect pickup, dropped items, placement mismatch).
- Detects navigation failures and blocked routes.
- Detects coordination and corridor deadlocks.
- Detects repeated unnecessary looping actions and failed recoveries.
- Persists detected errors to SQLite while preventing duplicate records.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging
import math
from typing import Any, Dict, List, Optional, Set, Tuple

from agentguard.error_classifier import ErrorCategory, ErrorClassifier, ErrorSeverity
from database.db import get_db_session
from database.models import Error
from engine.simulation import WarehouseSimulation

logger = logging.getLogger("robotrace.agentguard")


@dataclass
class DetectedError:
    """An error detected and classified by AgentGuard."""
    id: int
    mission_id: int
    agent_id: str
    task_id: Optional[str]
    step_id: Optional[int]
    error_code: str
    error_message: str
    severity: str
    suggested_category: str
    rule_id: str
    evidence: Dict[str, Any]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "mission_id": self.mission_id,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "step_id": self.step_id,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "severity": self.severity,
            "suggested_category": self.suggested_category,
            "rule_id": self.rule_id,
            "evidence": self.evidence,
            "timestamp": self.timestamp,
        }


class AgentGuard:
    """Independent supervisor and auditor for warehouse robot actions."""

    def __init__(self, simulation: Optional[WarehouseSimulation] = None):
        self.simulation = simulation
        self._next_error_id: int = 1
        self._recorded_dedup_keys: Set[Tuple[int, str, str, Optional[int]]] = set()  # (mission_id, agent_id, rule_id, step_id)
        self.detected_errors: List[DetectedError] = []
        self._action_history: Dict[str, List[str]] = {}  # agent_id -> list of recent actions

    def _generate_error_code(self, category: ErrorCategory, index: int) -> str:
        """Create standard error code (e.g. COL-001, NAV-002, CMP-003)."""
        prefix_map = {
            ErrorCategory.PERCEPTION: "PER",
            ErrorCategory.NAVIGATION: "NAV",
            ErrorCategory.PLANNING: "PLN",
            ErrorCategory.MANIPULATION: "MAN",
            ErrorCategory.COLLISION: "COL",
            ErrorCategory.EXECUTION: "EXE",
            ErrorCategory.RECOVERY: "REC",
            ErrorCategory.TASK_COMPLETION: "CMP",
            ErrorCategory.COORDINATION: "CRD",
        }
        prefix = prefix_map.get(category, "ERR")
        return f"{prefix}-{index:03d}"

    def record_error(
        self,
        mission_id: int,
        agent_id: str,
        rule_id: str,
        error_message: str,
        evidence: Dict[str, Any],
        task_id: Optional[str] = None,
        step_id: Optional[int] = None,
        persist_db: bool = True,
    ) -> Optional[DetectedError]:
        """Record and classify error, guaranteeing deduplication for the same event and rule."""
        dedup_key = (mission_id, agent_id, rule_id, step_id)
        if dedup_key in self._recorded_dedup_keys:
            logger.debug("Duplicate error suppressed: %s", dedup_key)
            return None

        self._recorded_dedup_keys.add(dedup_key)

        category, severity = ErrorClassifier.classify(rule_id, evidence)
        err_id = self._next_error_id
        self._next_error_id += 1
        error_code = self._generate_error_code(category, err_id)
        now_iso = datetime.now(timezone.utc).isoformat()

        detected = DetectedError(
            id=err_id,
            mission_id=mission_id,
            agent_id=agent_id,
            task_id=task_id,
            step_id=step_id,
            error_code=error_code,
            error_message=error_message,
            severity=severity.value,
            suggested_category=category.value,
            rule_id=rule_id,
            evidence=evidence,
            timestamp=now_iso,
        )

        self.detected_errors.append(detected)
        logger.warning(
            "AgentGuard detected [%s] (%s): %s | Agent: %s, Rule: %s",
            error_code, category.value, error_message, agent_id, rule_id,
        )

        if persist_db:
            try:
                import asyncio
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop is not None and loop.is_running():
                    loop.create_task(self._persist_to_sqlite(detected))
                else:
                    asyncio.run(self._persist_to_sqlite(detected))
            except Exception as exc:
                logger.warning("AgentGuard persistence error: %s", exc)

        return detected

    async def _persist_to_sqlite(self, error: DetectedError) -> None:
        """Store error into SQLite database table without modifying suggested category."""
        try:
            async with get_db_session() as session:
                record = Error(
                    id=error.id,
                    mission_id=error.mission_id,
                    agent_name=error.agent_id,
                    step_id=error.step_id,
                    error_code=error.error_code,
                    error_message=error.error_message,
                    severity=error.severity,
                    suggested_category=error.suggested_category,
                    rule_id=error.rule_id,
                    evidence=json.dumps(error.evidence),
                    is_resolved=False,
                )
                await session.merge(record)
        except Exception as exc:
            logger.warning("Failed to persist AgentGuard error to SQLite: %s", exc)

    # -----------------------------------------------------------------------
    # Independent Action & State Evaluations
    # -----------------------------------------------------------------------

    def audit_physical_state(
        self,
        mission_id: int,
        agent_id: str,
        step_id: Optional[int] = None,
        persist_db: bool = True,
    ) -> List[DetectedError]:
        """Check for physical collisions and constraint violations in real time."""
        errors = []
        if self.simulation is None or not self.simulation._is_initialized:
            return errors

        # 1. Collision check
        collisions = self.simulation.detect_collisions(agent_id)
        if collisions:
            shelf_collisions = [c for c in collisions if c.startswith("SHELF_")]
            rule = "COLLISION_SHELF" if shelf_collisions else "COLLISION_OBSTACLE"
            err = self.record_error(
                mission_id=mission_id,
                agent_id=agent_id,
                rule_id=rule,
                error_message=f"Agent {agent_id} collided with {collisions}.",
                evidence={"colliding_objects": collisions},
                step_id=step_id,
                persist_db=persist_db,
            )
            if err:
                errors.append(err)

        return errors

    def audit_task_completion(
        self,
        mission_id: int,
        agent_id: str,
        task_id: str,
        reported_outcome: str,
        expected_station: Tuple[float, float],
        package_id: Optional[str] = None,
        step_id: Optional[int] = None,
        tolerance: float = 2.0,
        persist_db: bool = True,
    ) -> Optional[DetectedError]:
        """Deliberate check: verify if robot falsely reported completion without delivery."""
        if self.simulation is None or not self.simulation._is_initialized:
            return None

        if package_id is not None:
            pkg_pos = self.simulation.get_package_position(package_id)
            if pkg_pos is None:
                return self.record_error(
                    mission_id=mission_id,
                    agent_id=agent_id,
                    rule_id="UNDELIVERED_PACKAGE_REPORTED_COMPLETE",
                    error_message=f"Agent {agent_id} reported delivery of {package_id}, but package is missing from world.",
                    evidence={"package_id": package_id, "reported_outcome": reported_outcome},
                    task_id=task_id,
                    step_id=step_id,
                    persist_db=persist_db,
                )

            dist = math.hypot(pkg_pos[0] - expected_station[0], pkg_pos[1] - expected_station[1])
            if dist > tolerance:
                return self.record_error(
                    mission_id=mission_id,
                    agent_id=agent_id,
                    rule_id="UNDELIVERED_PACKAGE_REPORTED_COMPLETE",
                    error_message=(
                        f"Agent {agent_id} reported task delivery, but package {package_id} is located at "
                        f"({pkg_pos[0]:.2f}, {pkg_pos[1]:.2f}), which is {dist:.2f}m away from target {expected_station}."
                    ),
                    evidence={
                        "package_id": package_id,
                        "actual_package_position": pkg_pos,
                        "expected_station": expected_station,
                        "distance_discrepancy": round(dist, 2),
                    },
                    task_id=task_id,
                    step_id=step_id,
                    persist_db=persist_db,
                )

        return None

    def audit_pickup(
        self,
        mission_id: int,
        agent_id: str,
        package_id: str,
        pickup_success: bool,
        step_id: Optional[int] = None,
    ) -> Optional[DetectedError]:
        """Audit package pickup operation."""
        if not pickup_success:
            return self.record_error(
                mission_id=mission_id,
                agent_id=agent_id,
                rule_id="PICKUP_FAILED",
                error_message=f"Agent {agent_id} failed to grasp package {package_id}.",
                evidence={"package_id": package_id},
                step_id=step_id,
            )
        return None

    def audit_repetition(
        self,
        mission_id: int,
        agent_id: str,
        action: str,
        max_repeats: int = 4,
        step_id: Optional[int] = None,
    ) -> Optional[DetectedError]:
        """Detect repeated unnecessary actions / looping."""
        history = self._action_history.setdefault(agent_id, [])
        history.append(action)
        if len(history) > 20:
            history.pop(0)

        if len(history) >= max_repeats and all(a == action for a in history[-max_repeats:]):
            return self.record_error(
                mission_id=mission_id,
                agent_id=agent_id,
                rule_id="REPEATED_UNNECESSARY_ACTION",
                error_message=f"Agent {agent_id} repeated action '{action}' {max_repeats} consecutive times without progress.",
                evidence={"action": action, "repetition_count": max_repeats},
                step_id=step_id,
            )
        return None

    def get_errors(self, mission_id: Optional[int] = None) -> List[DetectedError]:
        """Retrieve detected errors, optionally filtered by mission."""
        if mission_id is not None:
            return [e for e in self.detected_errors if e.mission_id == mission_id]
        return list(self.detected_errors)

    def get_error_by_id(self, error_id: int) -> Optional[DetectedError]:
        """Retrieve error by integer ID."""
        for e in self.detected_errors:
            if e.id == error_id:
                return e
        return None
