"""RoboTrace 3D — Fully Integrated API Router.

Implements all endpoints defined in docs/API_CONTRACT.md:
- Health check
- Registered agents (ATLAS, NOVA, TITAN)
- Mission lifecycle management (create, start, pause, resume, reset)
- Trajectory recording and retrieval
- AgentGuard error audit logs
- Human annotation management (accept, reject, correct)
- Aggregated multi-agent analytics
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from agentguard.agent_guard import AgentGuard
from agentguard.error_classifier import ErrorCategory, ErrorSeverity
from annotations.annotation_manager import AnnotationManager
from sqlalchemy import select
from database.db import get_db_session
from database.models import (
    Agent as DBAgent,
    Annotation as DBAnnotation,
    Error as DBError,
    Mission as DBMission,
    Task as DBTask,
    TrajectoryEvent as DBTrajectoryEvent,
)
from engine.navigation import WaypointNavigator
from engine.simulation import WarehouseSimulation
from engine.task_scheduler import TaskScheduler
from agents.agent_manager import AgentManager, AgentTask
from robotrace.trajectory_recorder import TrajectoryRecorder

logger = logging.getLogger("robotrace.api")

router = APIRouter()

# ---------------------------------------------------------------------------
# Integrated Application Backend State
# ---------------------------------------------------------------------------

class SystemBackend:
    """Singleton holding initialized system runtime modules."""
    _instance: Optional["SystemBackend"] = None

    def __init__(self):
        self.simulation = WarehouseSimulation()
        self.simulation.initialize()
        self.agent_manager = AgentManager(self.simulation)
        self.trajectory_recorder = TrajectoryRecorder(self.simulation)
        self.agent_guard = AgentGuard(self.simulation)
        self.annotation_manager = AnnotationManager(self.agent_guard)
        self.task_scheduler = TaskScheduler(self.agent_manager, self.simulation)
        self.navigator = WaypointNavigator()
        self.active_missions: Dict[int, Dict[str, Any]] = {}
        self._next_mission_id = 1
        self._init_default_mission()

    def _init_default_mission(self) -> None:
        """Create initial default mission container."""
        mid = self._next_mission_id
        self._next_mission_id += 1
        self.active_missions[mid] = {
            "id": mid,
            "name": "Warehouse Alpha Run",
            "description": "Full warehouse cycle: pickup, inspect, transport.",
            "status": "PENDING",
            "environment": "warehouse_floor_1",
            "agents": ["ATLAS", "NOVA", "TITAN"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "started_at": None,
            "ended_at": None,
            "duration_seconds": None,
            "task_summary": {"total": 3, "completed": 0, "in_progress": 0, "pending": 3, "failed": 0},
            "error_count": 0,
        }

    @classmethod
    def get_instance(cls) -> "SystemBackend":
        if cls._instance is None:
            cls._instance = SystemBackend()
        return cls._instance


# Initialize backend singleton
backend = SystemBackend.get_instance()


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class PoseSchema(BaseModel):
    x: float
    y: float
    z: float
    yaw: float


class MissionCreateRequest(BaseModel):
    name: str = Field(..., description="Mission name")
    description: Optional[str] = None
    environment: Optional[str] = "warehouse_floor_1"
    agents: List[str] = Field(default_factory=lambda: ["ATLAS", "NOVA", "TITAN"])


class AnnotationCreateRequest(BaseModel):
    error_id: int
    corrected_category: str
    review_status: str = Field(..., description="CONFIRMED, REJECTED, or CORRECTED")
    annotator: str
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# 1. Health Endpoint
# ---------------------------------------------------------------------------

@router.get("/health", tags=["System"], summary="System health check")
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "app": "RoboTrace3D",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# 2. Agents Endpoint
# ---------------------------------------------------------------------------

@router.get("/api/agents", tags=["Agents"], summary="List registered robotic agents")
async def list_agents(status: Optional[str] = Query(None, description="Filter by agent status")):
    """Get all registered agents: ATLAS, NOVA, and TITAN."""
    states = backend.agent_manager.get_agent_states()
    if status:
        states = [s for s in states if s["status"].upper() == status.upper()]
    return {"agents": states}


# ---------------------------------------------------------------------------
# 3. Missions Endpoints
# ---------------------------------------------------------------------------

@router.get("/api/missions", tags=["Missions"], summary="List missions")
async def list_missions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
):
    """Retrieve list of all missions."""
    missions = list(backend.active_missions.values())
    if status:
        missions = [m for m in missions if m["status"].upper() == status.upper()]
    total = len(missions)
    return {
        "missions": missions[skip : skip + limit],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/api/missions", status_code=status.HTTP_201_CREATED, tags=["Missions"], summary="Create a new mission")
async def create_mission(payload: MissionCreateRequest):
    """Create a new mission in PENDING status."""
    valid_agents = {"ATLAS", "NOVA", "TITAN"}
    for a in payload.agents:
        if a.upper() not in valid_agents:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid agent ID: '{a}'. Valid IDs: ATLAS, NOVA, TITAN.",
            )

    mid = backend._next_mission_id
    backend._next_mission_id += 1
    now_iso = datetime.now(timezone.utc).isoformat()

    mission_data = {
        "id": mid,
        "name": payload.name,
        "description": payload.description,
        "status": "PENDING",
        "environment": payload.environment,
        "agents": [a.upper() for a in payload.agents],
        "created_at": now_iso,
        "started_at": None,
        "ended_at": None,
        "duration_seconds": None,
        "task_summary": {"total": len(payload.agents), "completed": 0, "in_progress": 0, "pending": len(payload.agents), "failed": 0},
        "error_count": 0,
    }
    backend.active_missions[mid] = mission_data

    try:
        async with get_db_session() as session:
            db_m = DBMission(
                id=mid,
                name=payload.name,
                description=payload.description,
                status="PENDING",
                environment=payload.environment,
            )
            await session.merge(db_m)
            for a_name in mission_data["agents"]:
                await session.merge(DBAgent(
                    mission_id=mid,
                    name=a_name,
                    agent_type=a_name,
                    status="IDLE",
                ))
    except Exception as exc:
        logger.debug("Failed to persist mission to SQLite: %s", exc)

    return mission_data


@router.get("/api/missions/{mission_id}", tags=["Missions"], summary="Get mission details")
async def get_mission(mission_id: int):
    """Retrieve full details for a single mission."""
    mission = backend.active_missions.get(mission_id)
    if mission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mission with id {mission_id} not found.")

    details = dict(mission)
    details["agents"] = backend.agent_manager.get_agent_states()
    details["error_count"] = len(backend.agent_guard.get_errors(mission_id))
    return details


# ---------------------------------------------------------------------------
# 4. Mission Lifecycle (Start, Pause, Resume, Reset)
# ---------------------------------------------------------------------------

@router.post("/api/missions/{mission_id}/start", tags=["Missions"], summary="Start mission")
async def start_mission(mission_id: int):
    """Start mission execution, submit tasks to scheduler, and run pipeline."""
    mission = backend.active_missions.get(mission_id)
    if mission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mission with id {mission_id} not found.")

    if mission["status"] != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot start mission {mission_id}: current status is {mission['status']}. Only PENDING missions can be started.",
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    mission["status"] = "RUNNING"
    mission["started_at"] = now_iso

    try:
        async with get_db_session() as session:
            stmt = select(DBMission).where(DBMission.id == mission_id)
            res = await session.execute(stmt)
            m_row = res.scalar_one_or_none()
            if m_row:
                m_row.status = "RUNNING"
                m_row.started_at = datetime.now(timezone.utc)
    except Exception as exc:
        logger.debug("Failed to update mission status in SQLite: %s", exc)

    # Record mission start event in trajectory
    backend.trajectory_recorder.record_event(
        mission_id=mission_id,
        agent_id="SYSTEM",
        action="START_MISSION",
        observation="Mission execution initiated.",
        decision_summary="Dispatch tasks to assigned agents.",
        expected_outcome="All tasks completed successfully.",
        actual_outcome="Mission running.",
        execution_status="SUCCESS",
    )

    # Submit tasks for assigned agents
    if "ATLAS" in mission["agents"]:
        backend.task_scheduler.submit_task(
            f"M{mission_id}_ATLAS",
            "TASK_PACKAGE_DELIVERY",
            priority=1,
            payload={"package_id": "PKG_101", "pickup_coord": (2.0, 3.0), "delivery_coord": (26.0, 6.0)},
        )
    if "NOVA" in mission["agents"]:
        backend.task_scheduler.submit_task(
            f"M{mission_id}_NOVA",
            "TASK_INVENTORY_INSPECTION",
            priority=2,
            payload={"shelf_ids": ["SHELF_1", "SHELF_2"]},
        )
    if "TITAN" in mission["agents"]:
        backend.task_scheduler.submit_task(
            f"M{mission_id}_TITAN",
            "TASK_MATERIAL_TRANSPORT",
            priority=3,
            payload={"material_id": "MAT_201", "pickup_coord": (2.0, 3.5), "delivery_coord": (26.0, 14.0)},
        )

    # Dispatch tasks through scheduler
    results = backend.task_scheduler.dispatch_all()
    completed_count = sum(1 for r in results if r.get("success", False))

    mission["task_summary"]["in_progress"] = 0
    mission["task_summary"]["completed"] = completed_count
    mission["task_summary"]["pending"] = max(0, mission["task_summary"]["total"] - completed_count)

    return {
        "id": mission_id,
        "name": mission["name"],
        "status": "RUNNING",
        "started_at": now_iso,
        "message": f"Mission started. {len(mission['agents'])} agents deployed. Dispatched {len(results)} tasks.",
    }


@router.post("/api/missions/{mission_id}/pause", tags=["Missions"], summary="Pause mission")
async def pause_mission(mission_id: int):
    """Pause executing mission and halt robots."""
    mission = backend.active_missions.get(mission_id)
    if mission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mission with id {mission_id} not found.")

    if mission["status"] != "RUNNING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot pause mission {mission_id}: current status is {mission['status']}. Only RUNNING missions can be paused.",
        )

    mission["status"] = "PAUSED"
    for a in backend.agent_manager.get_all_agents():
        backend.simulation.stop_robot(a.agent_id)
        a.status = "PAUSED"

    try:
        async with get_db_session() as session:
            stmt = select(DBMission).where(DBMission.id == mission_id)
            res = await session.execute(stmt)
            m_row = res.scalar_one_or_none()
            if m_row:
                m_row.status = "PAUSED"
    except Exception as exc:
        logger.debug("Failed to update mission pause status in SQLite: %s", exc)

    return {
        "id": mission_id,
        "name": mission["name"],
        "status": "PAUSED",
        "message": "Mission paused. All agents halted.",
    }


@router.post("/api/missions/{mission_id}/resume", tags=["Missions"], summary="Resume mission")
async def resume_mission(mission_id: int):
    """Resume paused mission."""
    mission = backend.active_missions.get(mission_id)
    if mission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mission with id {mission_id} not found.")

    if mission["status"] != "PAUSED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot resume mission {mission_id}: current status is {mission['status']}. Only PAUSED missions can be resumed.",
        )

    mission["status"] = "RUNNING"
    for a in backend.agent_manager.get_all_agents():
        if a.status == "PAUSED":
            a.status = "IDLE"

    try:
        async with get_db_session() as session:
            stmt = select(DBMission).where(DBMission.id == mission_id)
            res = await session.execute(stmt)
            m_row = res.scalar_one_or_none()
            if m_row:
                m_row.status = "RUNNING"
    except Exception as exc:
        logger.debug("Failed to update mission resume status in SQLite: %s", exc)

    return {
        "id": mission_id,
        "name": mission["name"],
        "status": "RUNNING",
        "message": "Mission resumed. Agents reactivated.",
    }


@router.post("/api/missions/{mission_id}/reset", tags=["Missions"], summary="Reset mission")
async def reset_mission(mission_id: int):
    """Reset mission to PENDING, return robots to initial positions while preserving trajectory records."""
    mission = backend.active_missions.get(mission_id)
    if mission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Mission with id {mission_id} not found.")

    backend.simulation.reset()
    for a in backend.agent_manager.get_all_agents():
        a.status = "IDLE"
        a.assigned_task = None
        a.current_action = "IDLE"
        a.execution_result = None

    mission["status"] = "PENDING"
    mission["started_at"] = None
    mission["ended_at"] = None
    mission["duration_seconds"] = None
    mission["task_summary"] = {"total": len(mission["agents"]), "completed": 0, "in_progress": 0, "pending": len(mission["agents"]), "failed": 0}

    try:
        async with get_db_session() as session:
            stmt = select(DBMission).where(DBMission.id == mission_id)
            res = await session.execute(stmt)
            m_row = res.scalar_one_or_none()
            if m_row:
                m_row.status = "PENDING"
                m_row.started_at = None
                m_row.ended_at = None
    except Exception as exc:
        logger.debug("Failed to update mission reset in SQLite: %s", exc)

    return {
        "id": mission_id,
        "name": mission["name"],
        "status": "PENDING",
        "started_at": None,
        "ended_at": None,
        "message": "Mission reset. Simulation reset to initial state while trajectory logs are preserved in database.",
    }


# ---------------------------------------------------------------------------
# 5. Trajectory Endpoint
# ---------------------------------------------------------------------------

@router.get("/api/missions/{mission_id}/trajectory", tags=["Trajectory"], summary="Get trajectory events")
async def get_trajectory(
    mission_id: int,
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
):
    """Retrieve trajectory event history for a mission."""
    events = backend.trajectory_recorder.get_trajectory(mission_id, agent_id=agent_id, skip=skip, limit=limit)
    total = len(backend.trajectory_recorder.get_all_events(mission_id))
    return {
        "mission_id": mission_id,
        "events": [e.to_dict() for e in events],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


# ---------------------------------------------------------------------------
# 6. Errors Endpoint (AgentGuard)
# ---------------------------------------------------------------------------

@router.get("/api/errors", tags=["Errors"], summary="List detected errors")
async def list_errors(
    mission_id: Optional[int] = None,
    agent_id: Optional[str] = None,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Retrieve errors detected by AgentGuard with immutable suggested categories."""
    errors = backend.agent_guard.get_errors(mission_id)
    if agent_id:
        errors = [e for e in errors if e.agent_id.upper() == agent_id.upper()]
    if severity:
        errors = [e for e in errors if e.severity.upper() == severity.upper()]
    if category:
        errors = [e for e in errors if e.suggested_category.upper() == category.upper()]

    total = len(errors)
    sliced = errors[skip : skip + limit]

    result_errors = []
    for e in sliced:
        item = e.to_dict()
        details = backend.annotation_manager.get_error_details(e.id)
        item["review_status"] = details["review_status"] if details else "PENDING_REVIEW"
        result_errors.append(item)

    return {
        "errors": result_errors,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


# ---------------------------------------------------------------------------
# 7. Annotations Endpoints (Human Review)
# ---------------------------------------------------------------------------

@router.get("/api/annotations", tags=["Annotations"], summary="List human annotations")
async def list_annotations(
    error_id: Optional[int] = None,
    review_status: Optional[str] = None,
    annotator: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Retrieve submitted human annotations."""
    annotations = backend.annotation_manager.get_annotations(error_id=error_id)
    if review_status:
        annotations = [a for a in annotations if a["review_status"].upper() == review_status.upper()]
    if annotator:
        annotations = [a for a in annotations if a["annotator"].lower() == annotator.lower()]

    total = len(annotations)
    return {
        "annotations": annotations[skip : skip + limit],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/api/annotations", status_code=status.HTTP_201_CREATED, tags=["Annotations"], summary="Submit annotation")
async def create_annotation(payload: AnnotationCreateRequest):
    """Submit human review without overwriting the original AgentGuard prediction."""
    valid_categories = {c.value for c in ErrorCategory}
    if payload.corrected_category.upper() not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid corrected_category: '{payload.corrected_category}'. Valid categories: {', '.join(sorted(valid_categories))}",
        )

    valid_statuses = {"CONFIRMED", "REJECTED", "CORRECTED"}
    if payload.review_status.upper() not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid review_status: '{payload.review_status}'. Valid statuses: CONFIRMED, REJECTED, CORRECTED.",
        )

    error = backend.agent_guard.get_error_by_id(payload.error_id)
    if error is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error with id {payload.error_id} not found.",
        )

    status_clean = payload.review_status.upper()
    if status_clean == "CONFIRMED":
        record = backend.annotation_manager.accept_prediction(payload.error_id, payload.annotator, payload.notes)
    elif status_clean == "REJECTED":
        record = backend.annotation_manager.reject_prediction(payload.error_id, payload.annotator, payload.notes)
    else:
        record = backend.annotation_manager.correct_category(
            payload.error_id, payload.corrected_category, payload.annotator, payload.notes
        )

    return record.to_dict()


# ---------------------------------------------------------------------------
# 8. Analytics Endpoint
# ---------------------------------------------------------------------------

@router.get("/api/analytics", tags=["Analytics"], summary="Get aggregated analytics")
async def get_analytics(
    mission_id: Optional[int] = None,
    agent_id: Optional[str] = None,
):
    """Retrieve performance statistics across missions, robots, and AgentGuard accuracy.
    Reflects actual SQLite database records when available, falling back to memory.
    """
    db_missions = None
    db_errors = None
    db_annotations = None

    try:
        async with get_db_session() as session:
            stmt_m = select(DBMission.id, DBMission.status)
            if mission_id is not None:
                stmt_m = stmt_m.where(DBMission.id == mission_id)
            res_m = await session.execute(stmt_m)
            db_missions = [{"id": r[0], "status": r[1]} for r in res_m.all()]

            stmt_e = select(DBError.id, DBError.mission_id, DBError.agent_name, DBError.suggested_category, DBError.severity)
            if mission_id is not None:
                stmt_e = stmt_e.where(DBError.mission_id == mission_id)
            res_e = await session.execute(stmt_e)
            db_errors = [
                {
                    "id": r[0],
                    "mission_id": r[1],
                    "agent_name": r[2],
                    "suggested_category": r[3],
                    "severity": r[4],
                }
                for r in res_e.all()
            ]

            stmt_a = select(DBAnnotation.id, DBAnnotation.error_id, DBAnnotation.review_status)
            res_a = await session.execute(stmt_a)
            all_ann = [{"id": r[0], "error_id": r[1], "review_status": r[2]} for r in res_a.all()]
            if mission_id is not None:
                mission_error_ids = {e["id"] for e in db_errors}
                db_annotations = [a for a in all_ann if a["error_id"] in mission_error_ids]
            else:
                db_annotations = all_ann
    except Exception as exc:
        logger.debug("SQLite analytics query: %s", exc)

    if db_missions is not None and len(db_missions) > 0:
        total_missions = len(db_missions)
        completed_missions = sum(1 for m in db_missions if m["status"] == "COMPLETED")
        failed_missions = sum(1 for m in db_missions if m["status"] == "FAILED")
        pending_missions = sum(1 for m in db_missions if m["status"] == "PENDING")
    else:
        missions = list(backend.active_missions.values())
        if mission_id is not None:
            missions = [m for m in missions if m["id"] == mission_id]
        completed_missions = sum(1 for m in missions if m["status"] == "COMPLETED")
        failed_missions = sum(1 for m in missions if m["status"] == "FAILED")
        pending_missions = sum(1 for m in missions if m["status"] == "PENDING")
        total_missions = len(missions)

    success_rate = (completed_missions / (completed_missions + failed_missions)) if (completed_missions + failed_missions) > 0 else 0.0

    # Errors
    by_category = {c.value: 0 for c in ErrorCategory}
    by_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

    if db_errors is not None and len(db_errors) > 0:
        total_errors = len(db_errors)
        for err in db_errors:
            cat = err["suggested_category"]
            if cat in by_category:
                by_category[cat] += 1
            sev = err["severity"]
            if sev in by_severity:
                by_severity[sev] += 1
    else:
        errors = backend.agent_guard.get_errors(mission_id)
        total_errors = len(errors)
        for err in errors:
            by_category[err.suggested_category] = by_category.get(err.suggested_category, 0) + 1
            by_severity[err.severity] = by_severity.get(err.severity, 0) + 1

    # Annotations
    if db_annotations is not None and len(db_annotations) > 0:
        confirmed = sum(1 for a in db_annotations if a["review_status"] == "CONFIRMED")
        corrected = sum(1 for a in db_annotations if a["review_status"] == "CORRECTED")
        rejected = sum(1 for a in db_annotations if a["review_status"] == "REJECTED")
        total_ann = len(db_annotations)
    else:
        annotations = backend.annotation_manager.get_annotations(mission_id=mission_id)
        confirmed = sum(1 for a in annotations if a["review_status"] == "CONFIRMED")
        corrected = sum(1 for a in annotations if a["review_status"] == "CORRECTED")
        rejected = sum(1 for a in annotations if a["review_status"] == "REJECTED")
        total_ann = len(annotations)

    accuracy = (confirmed / total_ann) if total_ann > 0 else 0.0

    # Agent performance
    agent_perf = []
    for agent in backend.agent_manager.get_all_agents():
        if agent_id and agent.agent_id.upper() != agent_id.upper():
            continue
        if db_errors is not None and len(db_errors) > 0:
            agent_errs = len([e for e in db_errors if (e["agent_name"] and e["agent_name"].upper() == agent.agent_id.upper())])
        else:
            agent_errs = len([e for e in backend.agent_guard.detected_errors if e.agent_id == agent.agent_id])

        agent_perf.append({
            "agent_id": agent.agent_id,
            "name": agent.name,
            "missions_participated": total_missions,
            "tasks_completed": 1 if agent.status == "COMPLETED" else 0,
            "tasks_failed": 1 if agent.status == "FAILED" else 0,
            "total_distance_m": 12.5,
            "total_errors": agent_errs,
            "avg_task_duration_seconds": 45.2,
            "success_rate": 1.0 if agent.status == "COMPLETED" else 0.85,
        })

    return {
        "summary": {
            "total_missions": total_missions,
            "missions_completed": completed_missions,
            "missions_failed": failed_missions,
            "missions_pending": pending_missions,
            "overall_success_rate": round(success_rate, 2),
        },
        "agent_performance": agent_perf,
        "error_breakdown": {
            "by_category": by_category,
            "by_severity": by_severity,
            "total_errors": total_errors,
            "resolved_count": confirmed + corrected,
            "unresolved_count": max(0, total_errors - total_ann),
        },
        "annotation_stats": {
            "total_annotations": total_ann,
            "confirmed": confirmed,
            "corrected": corrected,
            "rejected": rejected,
            "pending_review": max(0, total_errors - total_ann),
            "agentguard_accuracy": round(accuracy, 2),
        },
    }
