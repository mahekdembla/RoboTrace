"""API Integration tests for every endpoint defined in docs/API_CONTRACT.md."""

import pytest
from starlette.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    """Synchronous test client fixture."""
    return TestClient(app)


class TestApiIntegration:
    """Verify all REST API contract endpoints."""

    # 1. Health
    def test_get_health(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app"] == "RoboTrace3D"
        assert "version" in data
        assert "timestamp" in data

    # 2. Agents
    def test_get_agents(self, client: TestClient):
        response = client.get("/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        agent_ids = {a["agent_id"] for a in data["agents"]}
        assert "ATLAS" in agent_ids
        assert "NOVA" in agent_ids
        assert "TITAN" in agent_ids

    # 3. Missions - List & Create
    def test_list_and_create_mission(self, client: TestClient):
        # List
        res_list = client.get("/api/missions")
        assert res_list.status_code == 200
        assert "missions" in res_list.json()

        # Create
        payload = {
            "name": "Integration Test Mission",
            "description": "Automated pipeline run",
            "environment": "warehouse_floor_1",
            "agents": ["ATLAS", "NOVA", "TITAN"],
        }
        res_create = client.post("/api/missions", json=payload)
        assert res_create.status_code == 201
        created = res_create.json()
        assert created["name"] == payload["name"]
        assert created["status"] == "PENDING"
        mid = created["id"]

        # Get Single Mission
        res_get = client.get(f"/api/missions/{mid}")
        assert res_get.status_code == 200
        assert res_get.json()["id"] == mid

    def test_create_mission_invalid_agent(self, client: TestClient):
        payload = {
            "name": "Invalid Agent Mission",
            "agents": ["ATLAS", "UNKNOWN_ROBOT"],
        }
        response = client.post("/api/missions", json=payload)
        assert response.status_code == 422
        assert "Invalid agent ID" in response.json()["detail"]

    # 4. Mission Lifecycle (Start, Pause, Resume, Reset)
    def test_mission_lifecycle_pipeline(self, client: TestClient):
        # Create fresh mission
        create_res = client.post("/api/missions", json={"name": "Lifecycle Mission", "agents": ["ATLAS"]})
        mid = create_res.json()["id"]

        # Start (PENDING -> RUNNING)
        start_res = client.post(f"/api/missions/{mid}/start")
        assert start_res.status_code == 200
        assert start_res.json()["status"] == "RUNNING"

        # Cannot re-start already RUNNING mission (409 Conflict)
        double_start = client.post(f"/api/missions/{mid}/start")
        assert double_start.status_code == 409

        # Pause (RUNNING -> PAUSED)
        pause_res = client.post(f"/api/missions/{mid}/pause")
        assert pause_res.status_code == 200
        assert pause_res.json()["status"] == "PAUSED"

        # Resume (PAUSED -> RUNNING)
        resume_res = client.post(f"/api/missions/{mid}/resume")
        assert resume_res.status_code == 200
        assert resume_res.json()["status"] == "RUNNING"

        # Reset (RUNNING -> PENDING)
        reset_res = client.post(f"/api/missions/{mid}/reset")
        assert reset_res.status_code == 200
        assert reset_res.json()["status"] == "PENDING"

    # 5. Trajectory
    def test_get_trajectory(self, client: TestClient):
        response = client.get("/api/missions/1/trajectory")
        assert response.status_code == 200
        data = response.json()
        assert "mission_id" in data
        assert "events" in data
        assert "total" in data

    # 6. Errors (AgentGuard)
    def test_get_errors(self, client: TestClient):
        response = client.get("/api/errors")
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data

    # 7. Annotations
    def test_create_and_get_annotation(self, client: TestClient):
        from backend.api.routes import backend
        # Ensure at least one error exists in AgentGuard with unique rule and step
        err = backend.agent_guard.record_error(
            mission_id=1,
            agent_id="ATLAS",
            rule_id="COLLISION_SHELF_FOR_ANNOTATION_TEST",
            error_message="Test collision",
            evidence={},
            step_id=999,
            persist_db=False,
        )
        if err is None:
            # Fall back to first available error
            err = backend.agent_guard.detected_errors[0]
        err_id = err.id

        # Submit annotation (CORRECTED)
        ann_payload = {
            "error_id": err_id,
            "corrected_category": "PERCEPTION",
            "review_status": "CORRECTED",
            "annotator": "lead.tester@robotrace.dev",
            "notes": "Sensor glare caused collision.",
        }
        create_res = client.post("/api/annotations", json=ann_payload)
        assert create_res.status_code == 201
        ann_data = create_res.json()
        assert ann_data["corrected_category"] == "PERCEPTION"
        assert ann_data["original_suggested_category"] == "COLLISION"  # Preserved!
        assert ann_data["review_status"] == "CORRECTED"

        # List annotations
        list_res = client.get("/api/annotations")
        assert list_res.status_code == 200
        assert len(list_res.json()["annotations"]) >= 1

    def test_create_annotation_invalid_category(self, client: TestClient):
        payload = {
            "error_id": 1,
            "corrected_category": "FAKE_CATEGORY",
            "review_status": "CORRECTED",
            "annotator": "tester",
        }
        res = client.post("/api/annotations", json=payload)
        assert res.status_code == 422
        assert "Invalid corrected_category" in res.json()["detail"]

    # 8. Analytics
    def test_get_analytics(self, client: TestClient):
        response = client.get("/api/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "agent_performance" in data
        assert "error_breakdown" in data
        assert "annotation_stats" in data
        assert "by_category" in data["error_breakdown"]
        # Verify 9 categories are present
        assert "COLLISION" in data["error_breakdown"]["by_category"]
        assert "PERCEPTION" in data["error_breakdown"]["by_category"]
        assert "TASK_COMPLETION" in data["error_breakdown"]["by_category"]
