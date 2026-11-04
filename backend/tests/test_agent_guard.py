"""Unit tests for AgentGuard independent error verification and classification."""

import logging
import pytest
from agentguard.agent_guard import AgentGuard
from agentguard.error_classifier import ErrorCategory, ErrorClassifier, ErrorSeverity
from engine.simulation import WarehouseSimulation

logger = logging.getLogger("test.agentguard")


@pytest.fixture
def sim():
    s = WarehouseSimulation()
    s.initialize()
    yield s
    s.shutdown()


class TestAgentGuard:
    """Test AgentGuard independent auditing and deterministic error classification."""

    def test_nine_error_categories_and_severities(self):
        """Verify all 9 standard error categories are classified deterministically."""
        # 1. COLLISION
        cat, sev = ErrorClassifier.classify("COLLISION_SHELF")
        assert cat == ErrorCategory.COLLISION
        assert sev == ErrorSeverity.HIGH

        # 2. TASK_COMPLETION
        cat, sev = ErrorClassifier.classify("UNDELIVERED_PACKAGE_REPORTED_COMPLETE")
        assert cat == ErrorCategory.TASK_COMPLETION
        assert sev == ErrorSeverity.HIGH

        # 3. MANIPULATION
        cat, sev = ErrorClassifier.classify("PICKUP_FAILED")
        assert cat == ErrorCategory.MANIPULATION
        assert sev == ErrorSeverity.HIGH

        # 4. NAVIGATION
        cat, sev = ErrorClassifier.classify("OFF_PATH")
        assert cat == ErrorCategory.NAVIGATION
        assert sev == ErrorSeverity.MEDIUM

        # 5. PERCEPTION
        cat, sev = ErrorClassifier.classify("SENSOR_MISREAD")
        assert cat == ErrorCategory.PERCEPTION
        assert sev == ErrorSeverity.MEDIUM

        # 6. PLANNING
        cat, sev = ErrorClassifier.classify("INCOMPATIBLE_TASK_ASSIGNED")
        assert cat == ErrorCategory.PLANNING
        assert sev == ErrorSeverity.HIGH

        # 7. RECOVERY
        cat, sev = ErrorClassifier.classify("FAILED_RECOVERY")
        assert cat == ErrorCategory.RECOVERY
        assert sev == ErrorSeverity.HIGH

        # 8. EXECUTION
        cat, sev = ErrorClassifier.classify("REPEATED_UNNECESSARY_ACTION")
        assert cat == ErrorCategory.EXECUTION
        assert sev == ErrorSeverity.MEDIUM

        # 9. COORDINATION
        cat, sev = ErrorClassifier.classify("SPATIAL_CONFLICT")
        assert cat == ErrorCategory.COORDINATION
        assert sev == ErrorSeverity.HIGH

    def test_error_deduplication(self, sim):
        """Verify duplicate errors for the same event and rule are suppressed."""
        guard = AgentGuard(sim)

        err1 = guard.record_error(
            mission_id=1,
            agent_id="ATLAS",
            rule_id="COLLISION_SHELF",
            error_message="Atlas hit shelf 1",
            evidence={"contact": "SHELF_1"},
            step_id=5,
            persist_db=False,
        )
        assert err1 is not None

        # Repeat same error with same mission, agent, rule, and step_id
        err2 = guard.record_error(
            mission_id=1,
            agent_id="ATLAS",
            rule_id="COLLISION_SHELF",
            error_message="Atlas hit shelf 1 again",
            evidence={"contact": "SHELF_1"},
            step_id=5,
            persist_db=False,
        )
        assert err2 is None  # Suppressed duplicate

        assert len(guard.detected_errors) == 1

    # -----------------------------------------------------------------------
    # Deliberate Failure Test 1: Robot collision with a shelf
    # -----------------------------------------------------------------------
    def test_deliberate_failure_1_collision_with_shelf(self, sim):
        """Deliberate Failure 1: Drive ATLAS directly into SHELF_1 and verify detection."""
        guard = AgentGuard(sim)

        # SHELF_1 is located at (8.0, 6.0). Drive ATLAS from (2.0, 2.0) towards shelf
        # Move ATLAS body close to shelf to cause physical collision
        # Command forward velocity directly towards shelf
        sim.set_robot_velocity("ATLAS", linear_velocity=2.5, angular_velocity=0.0)

        # Teleport ATLAS right in contact with SHELF_1 collision boundary (7.0, 6.0, 0.25)
        # Using the simulation API:
        p_engine = getattr(sim, "client_id")
        from engine.simulation import p
        p.resetBasePositionAndOrientation(
            sim.robot_bodies["ATLAS"],
            pos=[7.5, 6.0, 0.25],
            orn=[0.0, 0.0, 0.0, 1.0],
            physicsClientId=sim.client_id,
        )
        sim.step(5)

        # AgentGuard independently audits physical state
        detected_errors = guard.audit_physical_state(mission_id=1, agent_id="ATLAS", step_id=12)

        assert len(detected_errors) >= 1
        shelf_err = detected_errors[0]
        assert shelf_err.suggested_category == "COLLISION"
        assert shelf_err.severity == "HIGH"
        assert "SHELF_1" in str(shelf_err.evidence)
        logger.info("Deliberate Failure 1 PASSED: AgentGuard detected %s", shelf_err.error_code)

    # -----------------------------------------------------------------------
    # Deliberate Failure Test 2: Reports delivery without delivering package
    # -----------------------------------------------------------------------
    def test_deliberate_failure_2_false_delivery_report(self, sim):
        """Deliberate Failure 2: Robot reports task COMPLETED while package is still at origin."""
        guard = AgentGuard(sim)

        # PKG_101 is located at Pickup Station A (2.0, 3.0).
        # ATLAS falsely claims delivery at DELIVERY_A (26.0, 6.0)
        reported_station = (26.0, 6.0)

        error = guard.audit_task_completion(
            mission_id=1,
            agent_id="ATLAS",
            task_id="TASK_DELIVERY_01",
            reported_outcome="Package PKG_101 delivered to Delivery Station A successfully.",
            expected_station=reported_station,
            package_id="PKG_101",
            step_id=25,
            tolerance=2.0,
            persist_db=False if hasattr(guard, "_persist_to_sqlite") else None,
        )

        assert error is not None
        assert error.suggested_category == "TASK_COMPLETION"
        assert error.severity == "HIGH"
        assert "UNDELIVERED_PACKAGE_REPORTED_COMPLETE" in error.rule_id
        assert error.evidence["distance_discrepancy"] > 20.0  # Approx 24m away!
        logger.info("Deliberate Failure 2 PASSED: AgentGuard detected %s", error.error_code)
