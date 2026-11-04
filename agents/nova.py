"""RoboTrace 3D — NOVA Agent.

Role: Inventory Inspection
Deterministic rule-based agent responsible for:
1. Navigating sequentially to assigned warehouse shelves.
2. Inspecting shelf items (barcodes, counted quantities).
3. Comparing actual counted inventory against expected manifests.
4. Detecting discrepancies (missing items, overstock, wrong placements).
5. Generating structured inspection audit results.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from engine.navigation import NavigationError, WaypointNavigator
from engine.simulation import WarehouseSimulation

logger = logging.getLogger("robotrace.nova")


class NovaAgent:
    """NOVA — Autonomous Inventory Inspection Robot."""

    # Default ground truth warehouse shelf inventory database
    GROUND_TRUTH_INVENTORY: Dict[str, Dict[str, int]] = {
        "SHELF_1": {"ITEM_BEARING_A": 24, "ITEM_MOTOR_B": 10, "ITEM_SENSOR_C": 15},
        "SHELF_2": {"ITEM_BRACKET_D": 50, "ITEM_CABLE_E": 100},
        "SHELF_3": {"ITEM_CIRCUIT_F": 30, "ITEM_CHIP_G": 60},
        "SHELF_4": {"ITEM_SCREW_M4": 500, "ITEM_NUT_M4": 500},
        "SHELF_5": {"ITEM_BATTERY_12V": 12, "ITEM_CHARGER": 8},
        "SHELF_6": {"ITEM_CAMERA_MODULE": 18, "ITEM_LIDAR_MINI": 6},
    }

    # Shelf inspection staging coordinates (adjacent to each shelf)
    SHELF_ACCESS_COORDINATES: Dict[str, Tuple[float, float]] = {
        "SHELF_1": (6.0, 6.0),
        "SHELF_2": (6.0, 10.0),
        "SHELF_3": (6.0, 14.0),
        "SHELF_4": (18.0, 6.0),
        "SHELF_5": (18.0, 10.0),
        "SHELF_6": (18.0, 14.0),
    }

    def __init__(self, agent_id: str = "NOVA"):
        self.agent_id: str = agent_id
        self.name: str = "Nova"
        self.role: str = "Inventory inspection"
        self.status: str = "IDLE"  # IDLE, ASSIGNED, MOVING, WORKING, COMPLETED, FAILED, PAUSED
        self.assigned_task: Optional[Dict[str, Any]] = None
        self.current_action: Optional[str] = None
        self.execution_result: Optional[Dict[str, Any]] = None
        self.inspection_reports: List[Dict[str, Any]] = []
        self.battery_level: float = 100.0

    @property
    def position(self) -> Dict[str, float]:
        """Placeholder accessor; query simulation for physics source of truth."""
        return {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0}

    def get_state(self, simulation: Optional[WarehouseSimulation] = None) -> Dict[str, Any]:
        """Return full state representation."""
        pose = {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0}
        linear_v, angular_v = 0.0, 0.0
        if simulation is not None and simulation._is_initialized:
            try:
                x, y, z, yaw = simulation.get_robot_pose(self.agent_id)
                pose = {"x": round(x, 4), "y": round(y, 4), "z": round(z, 4), "yaw": round(yaw, 4)}
                linear_v, angular_v = simulation.get_robot_velocities(self.agent_id)
            except Exception:
                pass

        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "status": self.status,
            "current_pose": pose,
            "linear_velocity": round(linear_v, 4),
            "angular_velocity": round(angular_v, 4),
            "assigned_task": self.assigned_task,
            "current_action": self.current_action,
            "execution_result": self.execution_result,
            "reports_count": len(self.inspection_reports),
            "battery_level": self.battery_level,
        }

    # -----------------------------------------------------------------------
    # Core Deterministic Rule-Based Actions
    # -----------------------------------------------------------------------

    def navigate_to_shelf(
        self,
        shelf_id: str,
        navigator: WaypointNavigator,
        simulation: WarehouseSimulation,
    ) -> bool:
        """Navigate to inspection waypoint adjacent to the shelf."""
        coord = self.SHELF_ACCESS_COORDINATES.get(shelf_id, (6.0, 6.0))
        self.current_action = f"NAVIGATE_TO_SHELF({shelf_id}, coord={coord})"
        self.status = "MOVING"
        try:
            res = navigator.navigate_to(self.agent_id, coord, simulation)
            return res.get("success", False)
        except NavigationError as exc:
            self.status = "FAILED"
            self.execution_result = {"success": False, "error": str(exc)}
            logger.error("Nova failed to navigate to shelf %s: %s", shelf_id, exc)
            return False

    def inspect_inventory(self, shelf_id: str) -> Dict[str, int]:
        """Perform sensor scan and count physical inventory items on shelf."""
        self.current_action = f"SCAN_SHELF({shelf_id})"
        self.status = "WORKING"
        actual_items = self.GROUND_TRUTH_INVENTORY.get(shelf_id, {}).copy()
        logger.info("Nova scanned shelf %s: detected %d SKUs.", shelf_id, len(actual_items))
        return actual_items

    @staticmethod
    def compare_inventory(
        expected: Dict[str, int],
        actual: Dict[str, int],
    ) -> Dict[str, Any]:
        """Deterministic comparison between expected manifest and actual count."""
        discrepancies: List[Dict[str, Any]] = []
        all_skus = set(expected.keys()) | set(actual.keys())

        for sku in sorted(all_skus):
            exp_qty = expected.get(sku, 0)
            act_qty = actual.get(sku, 0)
            diff = act_qty - exp_qty
            if diff != 0:
                discrepancies.append({
                    "sku": sku,
                    "expected": exp_qty,
                    "actual": act_qty,
                    "difference": diff,
                    "status": "SHORTAGE" if diff < 0 else "SURPLUS",
                })

        return {
            "match": len(discrepancies) == 0,
            "discrepancies_count": len(discrepancies),
            "discrepancies": discrepancies,
        }

    def generate_inspection_result(
        self,
        shelf_id: str,
        expected: Dict[str, int],
        actual: Dict[str, int],
        comparison: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Assemble formal inspection audit record."""
        report = {
            "shelf_id": shelf_id,
            "agent_id": self.agent_id,
            "match": comparison["match"],
            "discrepancies": comparison["discrepancies"],
            "scanned_items_count": sum(actual.values()),
            "expected_items_count": sum(expected.values()),
        }
        self.inspection_reports.append(report)
        return report

    def execute_task(
        self,
        task: Dict[str, Any],
        simulation: WarehouseSimulation,
        navigator: WaypointNavigator,
    ) -> Dict[str, Any]:
        """Execute complete shelf inspection workflow."""
        self.assigned_task = task
        self.status = "ASSIGNED"
        shelf_ids = task.get("shelf_ids", ["SHELF_1"])
        expected_manifest = task.get("expected_manifest", {})

        results_by_shelf: List[Dict[str, Any]] = []

        for shelf_id in shelf_ids:
            # 1. Navigate to shelf
            if not self.navigate_to_shelf(shelf_id, navigator, simulation):
                return self.execution_result

            # 2. Inspect inventory
            actual = self.inspect_inventory(shelf_id)

            # 3. Compare with expected manifest
            expected_for_shelf = expected_manifest.get(shelf_id, actual)
            comparison = self.compare_inventory(expected_for_shelf, actual)

            # 4. Generate report
            report = self.generate_inspection_result(shelf_id, expected_for_shelf, actual, comparison)
            results_by_shelf.append(report)

        self.status = "COMPLETED"
        self.current_action = "IDLE"
        self.execution_result = {
            "success": True,
            "agent_id": self.agent_id,
            "task_id": task.get("id", "TASK_NOVA"),
            "shelves_inspected": shelf_ids,
            "reports": results_by_shelf,
            "total_discrepancies": sum(r["discrepancies_count"] if "discrepancies_count" in r else len(r["discrepancies"]) for r in results_by_shelf),
        }
        return self.execution_result

