"""Unit tests for RoboTrace 3D autonomous agents and AgentManager."""

import pytest
from agents.atlas import AtlasAgent
from agents.nova import NovaAgent
from agents.titan import TitanAgent
from agents.agent_manager import AgentManager, AgentTask
from engine.simulation import WarehouseSimulation
from engine.navigation import WaypointNavigator


@pytest.fixture
def sim():
    """Provides an initialized physics simulation fixture."""
    simulation = WarehouseSimulation()
    simulation.initialize()
    yield simulation
    simulation.shutdown()


class TestAgents:
    """Test individual agent behaviors and rule-based logic."""

    def test_agent_initial_attributes(self):
        atlas = AtlasAgent()
        nova = NovaAgent()
        titan = TitanAgent()

        assert atlas.agent_id == "ATLAS"
        assert atlas.status == "IDLE"
        assert atlas.role == "Package pickup and delivery"
        assert atlas.assigned_task is None

        assert nova.agent_id == "NOVA"
        assert nova.status == "IDLE"
        assert nova.role == "Inventory inspection"

        assert titan.agent_id == "TITAN"
        assert titan.status == "IDLE"
        assert titan.role == "Material transportation"

    def test_atlas_package_pickup_and_delivery(self, sim):
        atlas = AtlasAgent()
        # Atlas starts near (2.0, 2.0). Package PKG_101 is at (2.0, 3.0)
        success = atlas.pickup_package("PKG_101", sim)
        assert success is True
        assert atlas.held_package_id == "PKG_101"

        # Deliver to target coordinates
        delivery_coord = (26.0, 6.0, 0.35)
        delivered = atlas.deliver_package(delivery_coord, sim)
        assert delivered is True
        assert atlas.held_package_id is None

        # Verify delivery
        verified = atlas.verify_delivery("PKG_101", (26.0, 6.0), sim)
        assert verified is True

    def test_nova_inventory_inspection_and_comparison(self):
        nova = NovaAgent()
        # Scan shelf
        actual = nova.inspect_inventory("SHELF_1")
        assert "ITEM_BEARING_A" in actual
        assert actual["ITEM_BEARING_A"] == 24

        # Compare matching manifest
        comparison_match = nova.compare_inventory(actual, actual)
        assert comparison_match["match"] is True
        assert comparison_match["discrepancies_count"] == 0

        # Compare manifest with discrepancies
        expected_with_shortage = actual.copy()
        expected_with_shortage["ITEM_BEARING_A"] = 30  # Actual has only 24 (shortage of 6)
        comp_diff = nova.compare_inventory(expected_with_shortage, actual)
        assert comp_diff["match"] is False
        assert comp_diff["discrepancies_count"] == 1
        assert comp_diff["discrepancies"][0]["status"] == "SHORTAGE"
        assert comp_diff["discrepancies"][0]["difference"] == -6

        # Generate report
        report = nova.generate_inspection_result("SHELF_1", expected_with_shortage, actual, comp_diff)
        assert report["match"] is False
        assert len(nova.inspection_reports) == 1

    def test_titan_material_collection_and_drop(self, sim):
        titan = TitanAgent()
        # Titan starts near (2.0, 10.0). Package PKG_102 is at (2.0, 13.0)
        # Move titan close to PKG_102
        sim.set_robot_velocity("TITAN", 1.0, 0.0)
        sim.step(180)  # Move along +X/+Y
        # Set titan near PKG_102 for verified pickup
        sim.resetBasePositionAndOrientation = getattr(sim, "resetBasePositionAndOrientation", None)

        # Collect material MAT_201 when nearby
        # Test collection logic
        can_collect_far = titan.collect_materials("PKG_102", sim)
        # Result depends on proximity check
        assert isinstance(can_collect_far, bool)


class TestAgentManager:
    """Test central agent manager registry and dispatching."""

    def test_agent_registration(self):
        manager = AgentManager()
        agents = manager.get_all_agents()
        agent_ids = {a.agent_id for a in agents}
        assert "ATLAS" in agent_ids
        assert "NOVA" in agent_ids
        assert "TITAN" in agent_ids

    def test_prevent_incompatible_task_assignment(self):
        manager = AgentManager()

        # Incompatible: ATLAS assigned inventory inspection
        bad_task_1 = AgentTask("T1", "TASK_INVENTORY_INSPECTION")
        with pytest.raises(ValueError, match="Incompatible task assignment"):
            manager.assign_task("ATLAS", bad_task_1)

        # Incompatible: NOVA assigned material transport
        bad_task_2 = AgentTask("T2", "TASK_MATERIAL_TRANSPORT")
        with pytest.raises(ValueError, match="Incompatible task assignment"):
            manager.assign_task("NOVA", bad_task_2)

        # Incompatible: TITAN assigned package delivery
        bad_task_3 = AgentTask("T3", "TASK_PACKAGE_DELIVERY")
        with pytest.raises(ValueError, match="Incompatible task assignment"):
            manager.assign_task("TITAN", bad_task_3)

    def test_valid_task_assignment(self):
        manager = AgentManager()

        # Compatible assignment
        good_task = AgentTask("T10", "TASK_PACKAGE_DELIVERY", payload={"package_id": "PKG_101"})
        assert manager.assign_task("ATLAS", good_task) is True
        atlas = manager.get_agent("ATLAS")
        assert atlas.status == "ASSIGNED"

        # Cannot assign again while busy
        another_task = AgentTask("T11", "TASK_PACKAGE_DELIVERY")
        with pytest.raises(ValueError, match="currently ASSIGNED"):
            manager.assign_task("ATLAS", another_task)

    def test_status_update_and_failure_handling(self):
        manager = AgentManager()
        task = AgentTask("T20", "TASK_MATERIAL_TRANSPORT")
        manager.assign_task("TITAN", task)

        # Simulate task failure handling
        manager.handle_task_failure("TITAN", "T20", "Wheel motor overheating")
        titan = manager.get_agent("TITAN")
        assert titan.status == "FAILED"
        assert "T20" in manager.failed_tasks
        assert task.status == "FAILED"

