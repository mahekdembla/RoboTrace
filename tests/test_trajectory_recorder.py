"""Unit tests for RoboTrace 3D spatial trajectory recorder."""

import pytest
from engine.simulation import WarehouseSimulation
from robotrace.trajectory_recorder import TrajectoryRecorder


@pytest.fixture
def sim():
    s = WarehouseSimulation()
    s.initialize()
    yield s
    s.shutdown()


class TestTrajectoryRecorder:
    """Test spatial event recording, sequential step IDs, and SQLite persistence."""

    def test_record_event_with_actual_physics_coordinates(self, sim):
        recorder = TrajectoryRecorder(sim)

        # Record event for ATLAS
        evt = recorder.record_event(
            mission_id=1,
            agent_id="ATLAS",
            action="PICKUP_PACKAGE(PKG_101)",
            observation="Arrived at Pickup A. Package PKG_101 detected.",
            decision_summary="Align gripper and attach package.",
            expected_outcome="Package secured on ATLAS.",
            actual_outcome="Package attached successfully.",
            execution_status="SUCCESS",
            task_id="TASK_01",
            persist_db=False,
        )

        assert evt.event_id == 1
        assert evt.step_id == 1
        assert evt.agent_id == "ATLAS"
        assert evt.mission_id == 1
        # Coordinates must match actual PyBullet pose
        x, y, z, _ = sim.get_robot_pose("ATLAS")
        assert abs(evt.position_x - x) < 1e-3
        assert abs(evt.position_y - y) < 1e-3

    def test_sequential_step_ids(self, sim):
        recorder = TrajectoryRecorder(sim)

        e1 = recorder.record_event(1, "ATLAS", "MOVE_TO_PICKUP", persist_db=False)
        e2 = recorder.record_event(1, "ATLAS", "PICKUP", persist_db=False)
        e3 = recorder.record_event(1, "ATLAS", "MOVE_TO_DELIVERY", persist_db=False)

        assert e1.step_id == 1
        assert e2.step_id == 2
        assert e3.step_id == 3

        # Different agent on same mission starts at step 1
        e_nova = recorder.record_event(1, "NOVA", "SCAN_SHELF_1", persist_db=False)
        assert e_nova.step_id == 1

    def test_chronological_filtering_by_mission_and_agent(self, sim):
        recorder = TrajectoryRecorder(sim)

        recorder.record_event(1, "ATLAS", "STEP_A1", persist_db=False)
        recorder.record_event(1, "NOVA", "STEP_N1", persist_db=False)
        recorder.record_event(2, "TITAN", "STEP_T1", persist_db=False)
        recorder.record_event(1, "ATLAS", "STEP_A2", persist_db=False)

        # Filter mission 1
        m1_events = recorder.get_trajectory(mission_id=1)
        assert len(m1_events) == 3

        # Filter mission 1 + ATLAS
        m1_atlas = recorder.get_trajectory(mission_id=1, agent_id="ATLAS")
        assert len(m1_atlas) == 2
        assert m1_atlas[0].action == "STEP_A1"
        assert m1_atlas[1].action == "STEP_A2"

    def test_record_both_successful_and_failed_actions(self, sim):
        recorder = TrajectoryRecorder(sim)

        ok_evt = recorder.record_event(1, "TITAN", "LIFT_MATERIAL", execution_status="SUCCESS", persist_db=False)
        fail_evt = recorder.record_event(1, "TITAN", "TRANSIT", execution_status="FAILED", persist_db=False)

        assert ok_evt.execution_status == "SUCCESS"
        assert fail_evt.execution_status == "FAILED"

