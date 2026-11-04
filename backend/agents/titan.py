"""RoboTrace 3D — TITAN Agent.

Role: Material Transportation
Deterministic rule-based agent responsible for:
1. Navigating to staging/material collection area.
2. Collecting heavy raw materials or freight containers.
3. Transporting them across heavy-load transit corridors via A* navigation.
4. Dropping materials accurately at target manufacturing/storage stations.
"""

import logging
from typing import Any, Dict, Optional, Tuple

from engine.navigation import NavigationError, WaypointNavigator
from engine.simulation import WarehouseSimulation

logger = logging.getLogger("robotrace.titan")


class TitanAgent:
    """TITAN — Heavy Autonomous Material Transportation Robot."""

    def __init__(self, agent_id: str = "TITAN"):
        self.agent_id: str = agent_id
        self.name: str = "Titan"
        self.role: str = "Material transportation"
        self.status: str = "IDLE"  # IDLE, ASSIGNED, MOVING, WORKING, COMPLETED, FAILED, PAUSED
        self.assigned_task: Optional[Dict[str, Any]] = None
        self.current_action: Optional[str] = None
        self.execution_result: Optional[Dict[str, Any]] = None
        self.carried_material_id: Optional[str] = None
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
            "carried_material_id": self.carried_material_id,
            "battery_level": self.battery_level,
        }

    # -----------------------------------------------------------------------
    # Core Deterministic Rule-Based Actions
    # -----------------------------------------------------------------------

    def collect_materials(
        self,
        material_id: str,
        simulation: WarehouseSimulation,
    ) -> bool:
        """Lock heavy material onto Titan's flatbed via physics constraint."""
        self.current_action = f"COLLECT_MATERIAL({material_id})"
        self.status = "WORKING"
        success = simulation.attach_package(self.agent_id, material_id)
        if success:
            self.carried_material_id = material_id
            logger.info("Titan collected material %s.", material_id)
            return True
        else:
            self.status = "FAILED"
            self.execution_result = {
                "success": False,
                "error": f"Failed to collect material {material_id}. Titan must be in proximity.",
            }
            return False

    def transport(
        self,
        destination: Tuple[float, float],
        navigator: WaypointNavigator,
        simulation: WarehouseSimulation,
    ) -> bool:
        """Transport material across warehouse using A* pathfinding."""
        self.current_action = f"TRANSPORT_MATERIAL_TO({destination[0]}, {destination[1]})"
        self.status = "MOVING"
        try:
            res = navigator.navigate_to(self.agent_id, destination, simulation, max_speed=1.0)
            return res.get("success", False)
        except NavigationError as exc:
            self.status = "FAILED"
            self.execution_result = {"success": False, "error": str(exc)}
            logger.error("Titan transport failed: %s", exc)
            return False

    def drop_materials(
        self,
        destination_location: Tuple[float, float, float],
        simulation: WarehouseSimulation,
    ) -> bool:
        """Release and offload material onto destination bay."""
        if not self.carried_material_id:
            self.status = "FAILED"
            self.execution_result = {"success": False, "error": "No material loaded on Titan."}
            return False

        mat_id = self.carried_material_id
        self.current_action = f"DROP_MATERIAL({mat_id})"
        self.status = "WORKING"
        success = simulation.detach_package(self.agent_id, mat_id, drop_position=destination_location)
        if success:
            self.carried_material_id = None
            logger.info("Titan successfully offloaded material %s at %s.", mat_id, destination_location)
            return True
        return False

    def execute_task(
        self,
        task: Dict[str, Any],
        simulation: WarehouseSimulation,
        navigator: WaypointNavigator,
    ) -> Dict[str, Any]:
        """Execute complete material collection, transit, and dropoff workflow."""
        self.assigned_task = task
        self.status = "ASSIGNED"
        material_id = task.get("material_id", "MAT_201")
        pickup_coord = task.get("pickup_coord", (2.0, 3.5))
        delivery_coord = task.get("delivery_coord", (26.0, 14.0))
        delivery_z = task.get("delivery_z", 0.35)

        # 1. Move to material collection location
        if not self.transport(pickup_coord, navigator, simulation):
            return self.execution_result

        # 2. Collect material
        if not self.collect_materials(material_id, simulation):
            return self.execution_result

        # 3. Transport to drop station
        if not self.transport(delivery_coord, navigator, simulation):
            return self.execution_result

        # 4. Drop material at destination
        drop_pos = (delivery_coord[0], delivery_coord[1], delivery_z)
        if not self.drop_materials(drop_pos, simulation):
            return self.execution_result

        self.status = "COMPLETED"
        self.current_action = "IDLE"
        self.execution_result = {
            "success": True,
            "agent_id": self.agent_id,
            "task_id": task.get("id", "TASK_TITAN"),
            "material_id": material_id,
            "destination": delivery_coord,
        }
        return self.execution_result

