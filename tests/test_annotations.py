"""Unit tests for Human Annotation Manager."""

import pytest
from agentguard.agent_guard import AgentGuard
from annotations.annotation_manager import AnnotationManager
from engine.simulation import WarehouseSimulation


@pytest.fixture
def guard_with_errors():
    sim = WarehouseSimulation()
    sim.initialize()
    guard = AgentGuard(sim)

    # Pre-populate errors
    guard.record_error(
        mission_id=1,
        agent_id="ATLAS",
        rule_id="COLLISION_SHELF",
        error_message="Atlas collided with SHELF_1",
        evidence={"contact": "SHELF_1"},
        step_id=10,
        persist_db=False,
    )
    guard.record_error(
        mission_id=1,
        agent_id="TITAN",
        rule_id="PICKUP_FAILED",
        error_message="Titan failed to lift heavy beam",
        evidence={"material": "MAT_201"},
        step_id=15,
        persist_db=False,
    )
    yield guard
    sim.shutdown()


class TestAnnotationManager:
    """Test human annotation review lifecycle, accepting, rejecting, and correcting errors."""

    def test_retrieve_pending_errors(self, guard_with_errors):
        mgr = AnnotationManager(guard_with_errors)
        pending = mgr.get_pending_errors(mission_id=1)
        assert len(pending) == 2

    def test_accept_agentguard_prediction(self, guard_with_errors):
        mgr = AnnotationManager(guard_with_errors)
        error_id = 1
        record = mgr.accept_prediction(
            error_id=error_id,
            annotator="dr.chen@robotrace.dev",
            notes="Confirmed: clear shelf collision visible in logs.",
            persist_db=False,
        )

        assert record.review_status == "CONFIRMED"
        assert record.corrected_category == "COLLISION"
        assert record.original_suggested_category == "COLLISION"
        assert record.annotator == "dr.chen@robotrace.dev"

        # Check pending errors count reduced
        pending = mgr.get_pending_errors(mission_id=1)
        assert len(pending) == 1
        assert pending[0]["id"] == 2

    def test_reject_agentguard_prediction(self, guard_with_errors):
        mgr = AnnotationManager(guard_with_errors)
        error_id = 2
        record = mgr.reject_prediction(
            error_id=error_id,
            annotator="eng.reviewer@robotrace.dev",
            notes="False alarm: sensor reported false slip during intentional drop.",
            persist_db=False,
        )

        assert record.review_status == "REJECTED"
        assert record.corrected_category == "REJECTED"

    def test_correct_error_category_preserves_original(self, guard_with_errors):
        mgr = AnnotationManager(guard_with_errors)
        error_id = 2  # Originally MANIPULATION

        record = mgr.correct_category(
            error_id=error_id,
            corrected_category="PERCEPTION",
            annotator="lead.auditor@robotrace.dev",
            notes="Root cause was a vision calibration error, not mechanical gripper failure.",
            persist_db=False,
        )

        assert record.review_status == "CORRECTED"
        assert record.corrected_category == "PERCEPTION"
        assert record.original_suggested_category == "MANIPULATION"

        # Verify original error object remains unchanged!
        err = guard_with_errors.get_error_by_id(error_id)
        assert err.suggested_category == "MANIPULATION"  # Never overwritten!

    def test_invalid_category_raises_error(self, guard_with_errors):
        mgr = AnnotationManager(guard_with_errors)
        with pytest.raises(ValueError, match="Invalid corrected category"):
            mgr.correct_category(
                error_id=1,
                corrected_category="NON_EXISTENT_CATEGORY",
                annotator="test@robotrace.dev",
                persist_db=False,
            )

    def test_retrieve_annotations_by_mission(self, guard_with_errors):
        mgr = AnnotationManager(guard_with_errors)
        mgr.accept_prediction(1, "reviewer1", persist_db=False)
        mgr.correct_category(2, "PERCEPTION", "reviewer2", persist_db=False)

        annotations = mgr.get_annotations(mission_id=1)
        assert len(annotations) == 2
        assert annotations[0]["error_id"] == 1
        assert annotations[1]["error_id"] == 2

