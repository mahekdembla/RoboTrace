"""RoboTrace 3D — ATLAS Agent.

Role: Package Pickup & Delivery
Deterministic rule-based agent responsible for:
1. Navigating to pickup station.
2. Picking up the package via physics constraint.
3. Transporting it across the warehouse via A* waypoint navigation.
4. Delivering package onto destination station.
5. Verifying delivery success and location accuracy.
"""

import math
import logging
from typing import Any, Dict, Optional, Tuple

from engine.navigation import NavigationError, WaypointNavigator
from engine.simulation import WarehouseSimulation

logger = logging.getLogger("robotrace.atlas")


class AtlasAgent:
    """ATLAS — Autonomous Package Delivery Robot."""

    def __init__(self, agent_id: str = "ATLAS"):
        self.agent_id: str = agent_id
        self.name: str = "Atlas"
        self.role: str = "Package pickup and delivery"
        self.status: str = "IDLE"  # IDLE, ASSIGNED, MOVING, WORKING, COMPLETED, FAILED, PAUSED
        self.assigned_task: Optional[Dict[str, Any]] = None
        self.current_action: Optional[str] = None
        self.execution_result: Optional[Dict[str, Any]] = None
        self.held_package_id: Optional[str] = None
        self.battery_level: float = 100.0

    @property
    def position(self) -> Dict[str, float]:
        """Placeholder accessor; query simulation for physics source of truth."""
        return {"x": 0.0, "y": 0.0, "z": 0.0, "yaw": 0.0}

    def get_state(self, simulation: Optional[WarehouseSimulation] = None) -> Dict[str, Any]:
        """Return full state representation. Uses simulation as source of truth if provided."""
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
            "held_package_id": self.held_package_id,
            "battery_level": self.battery_level,
        }

    # -----------------------------------------------------------------------
    # Core Deterministic Rule-Based Actions
    # -----------------------------------------------------------------------

    def pickup_package(self, package_id: str, simulation: WarehouseSimulation) -> bool:
        """Physically attach package to robot body."""
        self.current_action = f"PICKUP_PACKAGE({package_id})"
        self.status = "WORKING"
        success = simulation.attach_package(self.agent_id, package_id)
        if success:
            self.held_package_id = package_id
            logger.info("Atlas successfully grasped package %s.", package_id)
            return True
        else:
            self.status = "FAILED"
            self.execution_result = {
                "success": False,
                "error": f"Failed to attach package {package_id}. Alignment or proximity issue.",
            }
            return False

    def transport(
        self,
        destination: Tuple[float, float],
        navigator: WaypointNavigator,
        simulation: WarehouseSimulation,
    ) -> bool:
        """Transport package to destination via A* waypoints."""
        self.current_action = f"TRANSPORT_TO({destination[0]}, {destination[1]})"
        self.status = "MOVING"
        try:
            res = navigator.navigate_to(self.agent_id, destination, simulation)
            return res.get("success", False)
        except NavigationError as exc:
            self.status = "FAILED"
            self.execution_result = {"success": False, "error": str(exc)}
            logger.error("Atlas navigation failed: %s", exc)
            return False

    def deliver_package(
        self,
        delivery_location: Tuple[float, float, float],
        simulation: WarehouseSimulation,
    ) -> bool:
        """Release and place the held package at target station."""
        if not self.held_package_id:
            self.status = "FAILED"
            self.execution_result = {"success": False, "error": "No package held to deliver."}
            return False

        self.current_action = f"DELIVER_PACKAGE({self.held_package_id})"
        self.status = "WORKING"
        pkg_id = self.held_package_id
        success = simulation.detach_package(self.agent_id, pkg_id, drop_position=delivery_location)
        if success:
            self.held_package_id = None
            logger.info("Atlas placed package %s at %s.", pkg_id, delivery_location)
            return True
        return False

    def verify_delivery(
        self,
        package_id: str,
        expected_station_coord: Tuple[float, float],
        simulation: WarehouseSimulation,
        tolerance: float = 2.0,
    ) -> bool:
        """Verify delivery by checking package proximity to destination station."""
        self.current_action = f"VERIFY_DELIVERY({package_id})"
        pkg_pos = simulation.get_package_position(package_id)
        if pkg_pos is None:
            self.status = "FAILED"
            self.execution_result = {"success": False, "error": f"Package {package_id} not found in world."}
            return False

        dist = math.hypot(pkg_pos[0] - expected_station_coord[0], pkg_pos[1] - expected_station_coord[1])
        if dist <= tolerance:
            logger.info("Atlas verified package %s delivered within tolerance (%.2fm).", package_id, dist)
            return True
        else:
            self.status = "FAILED"
            self.execution_result = {
                "success": False,
                "error": f"Delivery verification failed: distance {dist:.2f}m exceeds tolerance {tolerance}m.",
            }
            return False

    def execute_task(
        self,
        task: Dict[str, Any],
        simulation: WarehouseSimulation,
        navigator: WaypointNavigator,
    ) -> Dict[str, Any]:
        """Execute complete pickup, transport, delivery, and verification workflow."""
        self.assigned_task = task
        self.status = "ASSIGNED"
        package_id = task.get("package_id", "PKG_101")
        pickup_coord = task.get("pickup_coord", (2.0, 3.0))
        delivery_coord = task.get("delivery_coord", (26.0, 6.0))
        delivery_z = task.get("delivery_z", 0.35)

        # 1. Navigate to pickup location
        if not self.transport(pickup_coord, navigator, simulation):
            return self.execution_result

        # 2. Pick up package
        if not self.pickup_package(package_id, simulation):
            return self.execution_result

        # 3. Transport to destination
        if not self.transport(delivery_coord, navigator, simulation):
            return self.execution_result

        # 4. Deliver package
        drop_pos = (delivery_coord[0], delivery_coord[1], delivery_z)
        if not self.deliver_package(drop_pos, simulation):
            return self.execution_result

        # 5. Verify delivery
        if not self.verify_delivery(package_id, delivery_coord, simulation):
            return self.execution_result

        self.status = "COMPLETED"
        self.current_action = "IDLE"
        self.execution_result = {
            "success": True,
            "agent_id": self.agent_id,
            "task_id": task.get("id", "TASK_ATLAS"),
            "package_id": package_id,
            "delivery_location": delivery_coord,
            "verified": True,
        }
        return self.execution_result

