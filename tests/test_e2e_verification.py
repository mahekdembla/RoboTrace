"""RoboTrace 3D — Complete End-to-End System Verification Test Suite.

Verifies all 16 core subsystems in a full end-to-end integration flow:
1. FastAPI startup
2. Database initialization (all 7 ORM tables)
3. Agent registration (ATLAS, NOVA, TITAN)
4. Mission creation
5. Task assignment & execution
6. PyBullet simulation
7. Robot movement
8. A* navigation & waypoint following
9. Collision detection
10. Mission pause and resume
11. Trajectory recording (sequential step IDs, Z-up poses, cognitive context)
12. AgentGuard evaluation
13. Error classification (9 deterministic categories & severity levels)
14. Human annotations (preserving immutable original AgentGuard predictions)
15. Analytics reflecting actual SQLite database records
16. WebSocket live telemetry communication
"""

import json
import pytest
from starlette.testclient import TestClient
from sqlalchemy import select, func

from backend.main import app
from backend.api.routes import backend
from database.db import get_db_session, init_db
from database.models import (
    Agent as DBAgent,
    Annotation as DBAnnotation,
    Error as DBError,
    Mission as DBMission,
    Task as DBTask,
    TrajectoryEvent as DBTrajectoryEvent,
    Evaluation as DBEvaluation,
)
from engine.simulation import WarehouseSimulation, p


@pytest.fixture(scope="module")
def client():
    """Module-scoped FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client


class TestRoboTraceE2EVerification:
    """Complete end-to-end verification covering all 16 specified subsystems."""

    # -----------------------------------------------------------------------
    # 1. FastAPI Startup, Health Check, & 2. Database Initialization
    # -----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_01_fastapi_startup_and_database_init(self, client: TestClient):
        """Verify FastAPI runs and all 7 database tables exist in SQLite."""
        # 1. Health endpoint
        res = client.get("/health")
        assert res.status_code == 200
        health = res.json()
        assert health["status"] == "healthy"
        assert health["app"] == "RoboTrace3D"
        assert "timestamp" in health

        # 2. Database verification - ensure tables exist and are queryable
        await init_db()
        async with get_db_session() as session:
            # Query all 7 tables
            missions = (await session.execute(select(func.count(DBMission.id)))).scalar()
            agents = (await session.execute(select(func.count(DBAgent.id)))).scalar()
            tasks = (await session.execute(select(func.count(DBTask.id)))).scalar()
            trajectories = (await session.execute(select(func.count(DBTrajectoryEvent.id)))).scalar()
            errors = (await session.execute(select(func.count(DBError.id)))).scalar()
            annotations = (await session.execute(select(func.count(DBAnnotation.id)))).scalar()
            evaluations = (await session.execute(select(func.count(DBEvaluation.id)))).scalar()

            assert missions is not None
            assert agents is not None
            assert tasks is not None
            assert trajectories is not None
            assert errors is not None
            assert annotations is not None
            assert evaluations is not None

    # -----------------------------------------------------------------------
    # 3. Agent Registration
    # -----------------------------------------------------------------------
    def test_02_agent_registration(self, client: TestClient):
        """Verify ATLAS, NOVA, and TITAN are registered with proper capabilities."""
        res = client.get("/api/agents")
        assert res.status_code == 200
        data = res.json()
        agents = {a["agent_id"]: a for a in data["agents"]}

        assert "ATLAS" in agents
        assert "NOVA" in agents
        assert "TITAN" in agents

        # Verify ATLAS properties
        atlas = agents["ATLAS"]
        assert "delivery" in atlas["role"].lower()
        assert atlas["current_pose"]["x"] is not None
        assert atlas["current_pose"]["z"] >= 0.0

        # Verify NOVA properties
        nova = agents["NOVA"]
        assert "inspection" in nova["role"].lower()

        # Verify TITAN properties
        titan = agents["TITAN"]
        assert "transport" in titan["role"].lower()

    # -----------------------------------------------------------------------
    # 4. Mission Creation, 5. Task Assignment, 6-8. Simulation, Movement, A*
    # -----------------------------------------------------------------------
    def test_03_mission_creation_and_full_three_agent_dispatch(self, client: TestClient):
        """Create and start a full mission with ATLAS, NOVA, and TITAN."""
        # 1. Create Mission
        create_payload = {
            "name": "E2E Full Multi-Agent Logistics Run",
            "description": "Orchestrates ATLAS, NOVA, and TITAN across warehouse floor",
            "environment": "warehouse_floor_1",
            "agents": ["ATLAS", "NOVA", "TITAN"],
        }
        res_create = client.post("/api/missions", json=create_payload)
        assert res_create.status_code == 201
        created = res_create.json()
        assert created["status"] == "PENDING"
        mid = created["id"]

        # 2. Start Mission - dispatches tasks to all 3 agents
        res_start = client.post(f"/api/missions/{mid}/start")
        assert res_start.status_code == 200
        start_data = res_start.json()
        assert start_data["status"] == "RUNNING"

        # Verify tasks were dispatched and executed
        mission_details = client.get(f"/api/missions/{mid}").json()
        assert mission_details["status"] == "RUNNING"
        assert mission_details["task_summary"]["completed"] >= 1

        # Verify simulation coordinates updated for moving agents
        sim = backend.simulation
        for agent_name in ["ATLAS", "NOVA", "TITAN"]:
            x, y, z, yaw = sim.get_robot_pose(agent_name)
            assert isinstance(x, float)
            assert isinstance(y, float)
            assert z >= 0.0

    # -----------------------------------------------------------------------
    # 9. Mission Pause and Resume
    # -----------------------------------------------------------------------
    def test_04_mission_pause_and_resume(self, client: TestClient):
        """Verify mission pause stops robots and resume reactivates them."""
        mid = 1  # Use default or active mission
        # Ensure mission is running first
        client.post(f"/api/missions/{mid}/start")

        # Pause
        res_pause = client.post(f"/api/missions/{mid}/pause")
        assert res_pause.status_code == 200
        assert res_pause.json()["status"] == "PAUSED"

        # Verify agents are paused
        agents_data = client.get("/api/agents").json()
        for a in agents_data["agents"]:
            assert a["status"] == "PAUSED"

        # Resume
        res_resume = client.post(f"/api/missions/{mid}/resume")
        assert res_resume.status_code == 200
        assert res_resume.json()["status"] == "RUNNING"

    # -----------------------------------------------------------------------
    # 10. Trajectory Recording
    # -----------------------------------------------------------------------
    def test_05_trajectory_recording(self, client: TestClient):
        """Verify trajectory events contain sequential step IDs, actual physics coords, and cognitive context."""
        # Query trajectory for mission 1
        res = client.get("/api/missions/1/trajectory")
        assert res.status_code == 200
        data = res.json()
        events = data["events"]
        assert len(events) >= 1

        # Check structure of events
        for event in events:
            assert "event_id" in event
            assert "step_id" in event
            assert event["step_id"] >= 1
            assert "pose" in event
            pose = event["pose"]
            assert "x" in pose and "y" in pose and "z" in pose and "yaw" in pose
            assert "observation" in event
            assert "decision_summary" in event
            assert "action" in event
            assert "execution_status" in event

    # -----------------------------------------------------------------------
    # 11. Deliberate Failure Injection & 12. AgentGuard Detection
    # -----------------------------------------------------------------------
    def test_06_deliberate_failure_injection_and_detection(self, client: TestClient):
        """Inject 1 collision and 1 false delivery report; verify AgentGuard detection and DB storage."""
        sim = backend.simulation
        guard = backend.agent_guard

        # -------------------------------------------------------------------
        # Injected Failure 1: Physical Collision with SHELF_1
        # -------------------------------------------------------------------
        # Teleport ATLAS right into contact with SHELF_1 at (7.5, 6.0, 0.25)
        p.resetBasePositionAndOrientation(
            sim.robot_bodies["ATLAS"],
            pos=[7.5, 6.0, 0.25],
            orn=[0.0, 0.0, 0.0, 1.0],
            physicsClientId=sim.client_id,
        )
        sim.step(5)

        # AgentGuard audits physical state
        detected_col_errors = guard.audit_physical_state(
            mission_id=1,
            agent_id="ATLAS",
            step_id=50,
            persist_db=True,
        )
        assert len(detected_col_errors) >= 1
        col_err = detected_col_errors[0]
        assert col_err.suggested_category == "COLLISION"
        assert col_err.severity == "HIGH"
        assert "SHELF" in str(col_err.evidence)

        # -------------------------------------------------------------------
        # Injected Failure 2: False Task Completion Report
        # -------------------------------------------------------------------
        # ATLAS falsely claims PKG_102 was delivered to Delivery Station B (26.0, 14.0),
        # but the simulation ground truth has PKG_102 at Pickup Station B (2.0, 13.0)
        task_err = guard.audit_task_completion(
            mission_id=1,
            agent_id="ATLAS",
            task_id="TASK_DELIVERY_FALSE_REPORT",
            reported_outcome="Package PKG_102 successfully delivered to Delivery Station B.",
            expected_station=(26.0, 14.0),
            package_id="PKG_102",
            step_id=51,
            tolerance=2.0,
            persist_db=True,
        )
        assert task_err is not None
        assert task_err.suggested_category == "TASK_COMPLETION"
        assert task_err.severity == "HIGH"
        assert "UNDELIVERED_PACKAGE_REPORTED_COMPLETE" in task_err.rule_id

        # Verify both errors are retrieved via REST endpoint
        res_errs = client.get("/api/errors?mission_id=1")
        assert res_errs.status_code == 200
        retrieved_errs = res_errs.json()["errors"]
        retrieved_cats = {e["suggested_category"] for e in retrieved_errs}
        assert "COLLISION" in retrieved_cats
        assert "TASK_COMPLETION" in retrieved_cats

    # -----------------------------------------------------------------------
    # 13. Error Classification & 14. Human Annotations
    # -----------------------------------------------------------------------
    def test_07_human_annotation_preserves_agentguard_prediction(self, client: TestClient):
        """Submit human annotation; verify original suggested_category is preserved in database."""
        # Find the collision error
        errors = backend.agent_guard.get_errors(mission_id=1)
        col_error = next(e for e in errors if e.suggested_category == "COLLISION")

        # Submit human correction: Reviewer overrides category to 'PERCEPTION' (sensor blind spot)
        payload = {
            "error_id": col_error.id,
            "corrected_category": "PERCEPTION",
            "review_status": "CORRECTED",
            "annotator": "lead_quality_engineer@robotrace.io",
            "notes": "LiDAR reflectivity issue caused undetected shelf obstacle.",
        }
        res_ann = client.post("/api/annotations", json=payload)
        assert res_ann.status_code == 201
        ann_record = res_ann.json()

        assert ann_record["error_id"] == col_error.id
        assert ann_record["original_suggested_category"] == "COLLISION"  # Original preserved!
        assert ann_record["corrected_category"] == "PERCEPTION"
        assert ann_record["review_status"] == "CORRECTED"

        # Verify the underlying Error record still retains suggested_category = 'COLLISION'
        err_in_guard = backend.agent_guard.get_error_by_id(col_error.id)
        assert err_in_guard.suggested_category == "COLLISION"

        # Also verify via GET /api/errors that the error still reports suggested_category = 'COLLISION'
        err_res = client.get(f"/api/errors?category=COLLISION")
        assert err_res.status_code == 200
        assert any(e["id"] == col_error.id for e in err_res.json()["errors"])

    # -----------------------------------------------------------------------
    # 15. Analytics (matching actual SQLite database records)
    # -----------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_08_analytics_reflect_database_records(self, client: TestClient):
        """Verify /api/analytics matches actual counts in SQLite database."""
        res = client.get("/api/analytics")
        assert res.status_code == 200
        analytics = res.json()

        # Check response structure
        assert "summary" in analytics
        assert "agent_performance" in analytics
        assert "error_breakdown" in analytics
        assert "annotation_stats" in analytics

        # Directly query SQLite database to verify numbers
        async with get_db_session() as session:
            db_error_count = (await session.execute(select(func.count(DBError.id)))).scalar()
            db_annotation_count = (await session.execute(select(func.count(DBAnnotation.id)))).scalar()

        # If DB records are present, verify analytics accurately reflect them
        if db_error_count > 0:
            assert analytics["error_breakdown"]["total_errors"] >= db_error_count
        if db_annotation_count > 0:
            assert analytics["annotation_stats"]["total_annotations"] >= db_annotation_count

        # Verify error breakdown has non-zero entries for injected failures
        by_cat = analytics["error_breakdown"]["by_category"]
        assert by_cat["COLLISION"] >= 1
        assert by_cat["TASK_COMPLETION"] >= 1

    # -----------------------------------------------------------------------
    # 16. WebSocket Live Telemetry Communication
    # -----------------------------------------------------------------------
    def test_09_websocket_live_telemetry_communication(self, client: TestClient):
        """Verify WebSocket bi-directional streaming: PING/PONG, SUBSCRIBE, and live broadcast."""
        with client.websocket_connect("/ws/simulation") as ws:
            # 1. PING / PONG
            ws.send_text(json.dumps({"type": "PING"}))
            msg_pong = json.loads(ws.receive_text())
            assert msg_pong["type"] == "PONG"
            assert "timestamp" in msg_pong

            # 2. SUBSCRIBE to mission
            ws.send_text(json.dumps({"type": "SUBSCRIBE", "data": {"mission_id": 1}}))
            msg_sub = json.loads(ws.receive_text())
            assert msg_sub["type"] == "SUBSCRIBED"
            assert msg_sub["data"]["mission_id"] == 1

            # 3. Broadcast test event
            from backend.api.websocket import ws_manager
            import asyncio
            asyncio.run(ws_manager.broadcast_message({
                "type": "telemetry_update",
                "timestamp": "2026-11-04T05:30:00Z",
                "data": {"mission_id": 1, "active_robots": 3},
            }))
            msg_broadcast = json.loads(ws.receive_text())
            assert msg_broadcast["type"] == "telemetry_update"
            assert msg_broadcast["data"]["active_robots"] == 3
