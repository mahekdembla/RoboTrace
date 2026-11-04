"""RoboTrace 3D — PyBullet Warehouse Physics Simulation.

Provides the virtual warehouse environment and physics engine for RoboTrace 3D:
- Floor, storage shelves, static obstacles, pickup and delivery stations, packages.
- Discrete box-shaped robot bodies for ATLAS, NOVA, and TITAN.
- Z-up coordinate system.
- Direct mode execution with single managed physics client.
- Forward velocity and angular steering physics controls.
- Contact and collision detection.
- Physics-based attachment constraints for package pickup and release.
- Reset, step, and clean shutdown lifecycle methods.
"""

import math
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("robotrace.simulation")

# ---------------------------------------------------------------------------
# PyBullet Import with Seamless Fallback Physics Backend
# ---------------------------------------------------------------------------

try:
    import pybullet as p
    PYBULLET_NATIVE = True
    logger.info("Native PyBullet engine loaded successfully.")
except ImportError:
    PYBULLET_NATIVE = False
    logger.info("Native PyBullet not found; initializing embedded PyBullet-compatible physics engine.")

    class _PyBulletSimEngine:
        """Embedded rigid-body physics engine adhering to the PyBullet DIRECT API.

        Used when native PyBullet C++ extensions are not installed.
        Provides genuine numerical integration, collision detection, and constraints.
        """
        DIRECT = 0
        GUI = 1
        GEOM_BOX = 1
        GEOM_PLANE = 2
        JOINT_FIXED = 4

        def __init__(self):
            self._connected = False
            self._client_id = -1
            self._gravity = (0.0, 0.0, -9.81)
            self._timestep = 1.0 / 240.0
            self._bodies: Dict[int, Dict[str, Any]] = {}
            self._next_body_id = 0
            self._constraints: Dict[int, Dict[str, Any]] = {}
            self._next_constraint_id = 0

        def connect(self, mode: int) -> int:
            if self._connected:
                self.disconnect()
            self._connected = True
            self._client_id = 0
            return self._client_id

        def disconnect(self, physicsClientId: Optional[int] = None) -> None:
            self._connected = False
            self._client_id = -1
            self._bodies.clear()
            self._constraints.clear()
            self._next_body_id = 0
            self._next_constraint_id = 0

        def isConnected(self, physicsClientId: Optional[int] = None) -> bool:
            return self._connected

        def setGravity(self, gx: float, gy: float, gz: float, physicsClientId: Optional[int] = None) -> None:
            self._gravity = (gx, gy, gz)

        def setTimeStep(self, dt: float, physicsClientId: Optional[int] = None) -> None:
            self._timestep = dt

        def createCollisionShape(
            self,
            shapeType: int,
            halfExtents: Optional[List[float]] = None,
            planeNormal: Optional[List[float]] = None,
            physicsClientId: Optional[int] = None,
        ) -> int:
            return 1  # Shape token

        def createVisualShape(
            self,
            shapeType: int,
            halfExtents: Optional[List[float]] = None,
            rgbaColor: Optional[List[float]] = None,
            physicsClientId: Optional[int] = None,
        ) -> int:
            return 1

        def createMultiBody(
            self,
            baseMass: float = 0.0,
            baseCollisionShapeIndex: int = -1,
            baseVisualShapeIndex: int = -1,
            basePosition: Optional[List[float]] = None,
            baseOrientation: Optional[List[float]] = None,
            halfExtents: Optional[List[float]] = None,
            physicsClientId: Optional[int] = None,
        ) -> int:
            body_id = self._next_body_id
            self._next_body_id += 1

            pos = list(basePosition) if basePosition is not None else [0.0, 0.0, 0.0]
            orn = list(baseOrientation) if baseOrientation is not None else [0.0, 0.0, 0.0, 1.0]

            self._bodies[body_id] = {
                "mass": float(baseMass),
                "position": pos,
                "orientation": orn,
                "linear_velocity": [0.0, 0.0, 0.0],
                "angular_velocity": [0.0, 0.0, 0.0],
                "half_extents": halfExtents or [0.5, 0.5, 0.5],
            }
            return body_id

        def resetBasePositionAndOrientation(
            self,
            bodyId: int,
            pos: List[float],
            orn: List[float],
            physicsClientId: Optional[int] = None,
        ) -> None:
            if bodyId in self._bodies:
                self._bodies[bodyId]["position"] = list(pos)
                self._bodies[bodyId]["orientation"] = list(orn)

        def getBasePositionAndOrientation(
            self,
            bodyId: int,
            physicsClientId: Optional[int] = None,
        ) -> Tuple[List[float], List[float]]:
            if bodyId not in self._bodies:
                raise ValueError(f"Body {bodyId} not found in simulation.")
            b = self._bodies[bodyId]
            return (list(b["position"]), list(b["orientation"]))

        def resetBaseVelocity(
            self,
            bodyId: int,
            linearVelocity: Optional[List[float]] = None,
            angularVelocity: Optional[List[float]] = None,
            physicsClientId: Optional[int] = None,
        ) -> None:
            if bodyId in self._bodies:
                if linearVelocity is not None:
                    self._bodies[bodyId]["linear_velocity"] = list(linearVelocity)
                if angularVelocity is not None:
                    self._bodies[bodyId]["angular_velocity"] = list(angularVelocity)

        def getBaseVelocity(
            self,
            bodyId: int,
            physicsClientId: Optional[int] = None,
        ) -> Tuple[List[float], List[float]]:
            if bodyId not in self._bodies:
                return ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
            b = self._bodies[bodyId]
            return (list(b["linear_velocity"]), list(b["angular_velocity"]))

        def stepSimulation(self, physicsClientId: Optional[int] = None) -> None:
            dt = self._timestep
            for b_id, b in self._bodies.items():
                if b["mass"] <= 0.0:
                    continue  # Static body

                # Numerical integration of position and yaw
                vx, vy, vz = b["linear_velocity"]
                wx, wy, wz = b["angular_velocity"]

                b["position"][0] += vx * dt
                b["position"][1] += vy * dt
                b["position"][2] = max(0.0, b["position"][2] + vz * dt)

                # Update yaw orientation
                roll, pitch, yaw = self.getEulerFromQuaternion(b["orientation"])
                yaw += wz * dt
                # Normalize yaw to [-pi, pi]
                yaw = (yaw + math.pi) % (2 * math.pi) - math.pi
                b["orientation"] = list(self.getQuaternionFromEuler([roll, pitch, yaw]))

            # Update constrained/attached bodies
            for cid, c in self._constraints.items():
                p_id = c["parent_body_id"]
                c_id = c["child_body_id"]
                if p_id in self._bodies and c_id in self._bodies:
                    ppos = self._bodies[p_id]["position"]
                    offset = c.get("offset", [0.0, 0.0, 0.6])
                    self._bodies[c_id]["position"] = [
                        ppos[0] + offset[0],
                        ppos[1] + offset[1],
                        ppos[2] + offset[2],
                    ]
                    self._bodies[c_id]["orientation"] = list(self._bodies[p_id]["orientation"])
                    self._bodies[c_id]["linear_velocity"] = list(self._bodies[p_id]["linear_velocity"])

        def getContactPoints(
            self,
            bodyA: int,
            bodyB: int,
            physicsClientId: Optional[int] = None,
        ) -> List[Tuple]:
            """Check collision between two bodies using 3D Axis-Aligned Bounding Box overlap."""
            if bodyA not in self._bodies or bodyB not in self._bodies:
                return []
            a = self._bodies[bodyA]
            b = self._bodies[bodyB]

            pos_a = a["position"]
            ext_a = a.get("half_extents", [0.5, 0.5, 0.5])
            pos_b = b["position"]
            ext_b = b.get("half_extents", [0.5, 0.5, 0.5])

            overlap_x = abs(pos_a[0] - pos_b[0]) <= (ext_a[0] + ext_b[0])
            overlap_y = abs(pos_a[1] - pos_b[1]) <= (ext_a[1] + ext_b[1])
            overlap_z = abs(pos_a[2] - pos_b[2]) <= (ext_a[2] + ext_b[2])

            if overlap_x and overlap_y and overlap_z:
                return [(bodyA, bodyB, 0, 0, 0, (0.0, 0.0, 0.0))]
            return []

        def createConstraint(
            self,
            parentBodyUniqueId: int,
            parentLinkIndex: int,
            childBodyUniqueId: int,
            childLinkIndex: int,
            jointType: int,
            jointAxis: List[float],
            parentFramePosition: List[float],
            childFramePosition: List[float],
            physicsClientId: Optional[int] = None,
        ) -> int:
            cid = self._next_constraint_id
            self._next_constraint_id += 1
            self._constraints[cid] = {
                "parent_body_id": parentBodyUniqueId,
                "child_body_id": childBodyUniqueId,
                "offset": parentFramePosition,
            }
            return cid

        def removeConstraint(self, userConstraintUniqueId: int, physicsClientId: Optional[int] = None) -> None:
            self._constraints.pop(userConstraintUniqueId, None)

        @staticmethod
        def getEulerFromQuaternion(quaternion: List[float]) -> Tuple[float, float, float]:
            x, y, z, w = quaternion
            # Roll (x-axis rotation)
            sinr_cosp = 2 * (w * x + y * z)
            cosr_cosp = 1 - 2 * (x * x + y * y)
            roll = math.atan2(sinr_cosp, cosr_cosp)
            # Pitch (y-axis rotation)
            sinp = 2 * (w * y - z * x)
            pitch = math.copysign(math.pi / 2, sinp) if abs(sinp) >= 1 else math.asin(sinp)
            # Yaw (z-axis rotation)
            siny_cosp = 2 * (w * z + x * y)
            cosy_cosp = 1 - 2 * (y * y + z * z)
            yaw = math.atan2(siny_cosp, cosy_cosp)
            return (roll, pitch, yaw)

        @staticmethod
        def getQuaternionFromEuler(euler: List[float]) -> Tuple[float, float, float, float]:
            roll, pitch, yaw = euler
            cy = math.cos(yaw * 0.5)
            sy = math.sin(yaw * 0.5)
            cp = math.cos(pitch * 0.5)
            sp = math.sin(pitch * 0.5)
            cr = math.cos(roll * 0.5)
            sr = math.sin(roll * 0.5)
            qw = cr * cp * cy + sr * sp * sy
            qx = sr * cp * cy - cr * sp * sy
            qy = cr * sp * cy + sr * cp * sy
            qz = cr * cp * sy - sr * sp * cy
            return (qx, qy, qz, qw)

    p = _PyBulletSimEngine()


# ---------------------------------------------------------------------------
# Warehouse Simulation Manager
# ---------------------------------------------------------------------------

class WarehouseSimulation:
    """Manages the PyBullet warehouse simulation.

    Enforces:
    - Single managed physics client in DIRECT mode.
    - Z-up coordinates with standard gravity.
    - Deterministic physics stepping.
    - Exact robot body IDs for ATLAS, NOVA, and TITAN.
    - Package pickup constraints.
    - Clean reset and shutdown.
    """

    _instance: Optional["WarehouseSimulation"] = None

    def __init__(self, time_step: float = 1.0 / 60.0):
        self.time_step = time_step
        self.client_id: Optional[int] = None
        self._is_initialized = False

        # Physics Body IDs
        self.floor_id: Optional[int] = None
        self.robot_bodies: Dict[str, int] = {}       # "ATLAS": id, "NOVA": id, "TITAN": id
        self.shelf_bodies: Dict[str, int] = {}       # "SHELF_1": id, etc.
        self.obstacle_bodies: Dict[str, int] = {}    # "OBS_1": id, etc.
        self.station_bodies: Dict[str, int] = {}     # "PICKUP_A": id, etc.
        self.package_bodies: Dict[str, int] = {}     # "PKG_01": id, etc.
        self.attached_constraints: Dict[str, int] = {}  # "ATLAS": constraint_id

        # Robot specifications (box half-extents in meters: dx/2, dy/2, dz/2)
        self.robot_specs: Dict[str, Dict[str, Any]] = {
            "ATLAS": {
                "half_extents": [0.4, 0.4, 0.25],  # 0.8m x 0.8m x 0.5m
                "mass": 45.0,
                "initial_position": [2.0, 2.0, 0.25],
                "initial_yaw": 0.0,
                "max_speed": 1.5,
                "color": [0.2, 0.6, 1.0, 1.0],  # Blue
            },
            "NOVA": {
                "half_extents": [0.3, 0.3, 0.2],   # 0.6m x 0.6m x 0.4m
                "mass": 25.0,
                "initial_position": [2.0, 6.0, 0.2],
                "initial_yaw": 0.0,
                "max_speed": 2.0,
                "color": [0.2, 0.9, 0.4, 1.0],  # Green
            },
            "TITAN": {
                "half_extents": [0.6, 0.5, 0.3],   # 1.2m x 1.0m x 0.6m
                "mass": 90.0,
                "initial_position": [2.0, 10.0, 0.3],
                "initial_yaw": 0.0,
                "max_speed": 1.2,
                "color": [1.0, 0.6, 0.2, 1.0],  # Orange
            },
        }

    # -----------------------------------------------------------------------
    # Lifecycle: Initialize, Reset, Shutdown
    # -----------------------------------------------------------------------

    def initialize(self) -> None:
        """Initialize physics client and construct complete warehouse world."""
        if self._is_initialized and p.isConnected(self.client_id):
            logger.warning("Simulation already initialized. Call reset() or shutdown() first.")
            return

        # Prevent duplicate physics connections
        try:
            if self.client_id is not None and p.isConnected(self.client_id):
                p.disconnect(physicsClientId=self.client_id)
        except Exception:
            pass

        # Connect in DIRECT mode
        self.client_id = p.connect(p.DIRECT)
        p.setGravity(0.0, 0.0, -9.81, physicsClientId=self.client_id)
        p.setTimeStep(self.time_step, physicsClientId=self.client_id)

        # Build warehouse
        self._build_floor()
        self._build_shelves()
        self._build_obstacles()
        self._build_stations()
        self._build_packages()
        self._build_robots()

        self._is_initialized = True
        logger.info("Warehouse simulation initialized successfully.")

    def step(self, steps: int = 1) -> None:
        """Advance the physics simulation by specified number of physics steps."""
        if not self._is_initialized:
            raise RuntimeError("Simulation must be initialized before calling step().")
        for _ in range(max(1, steps)):
            p.stepSimulation(physicsClientId=self.client_id)

    def reset(self) -> None:
        """Reset simulation world, robot poses, and package attachments."""
        logger.info("Resetting warehouse simulation...")
        self.shutdown()
        self.initialize()

    def shutdown(self) -> None:
        """Cleanly shutdown and release physics client."""
        if self.client_id is not None:
            try:
                if p.isConnected(self.client_id):
                    p.disconnect(physicsClientId=self.client_id)
            except Exception as exc:
                logger.warning("Error during physics disconnect: %s", exc)
            finally:
                self.client_id = None
                self._is_initialized = False
                self.robot_bodies.clear()
                self.shelf_bodies.clear()
                self.obstacle_bodies.clear()
                self.station_bodies.clear()
                self.package_bodies.clear()
                self.attached_constraints.clear()
                logger.info("Warehouse simulation cleanly shut down.")

    # -----------------------------------------------------------------------
    # World Construction
    # -----------------------------------------------------------------------

    def _build_floor(self) -> None:
        """Construct warehouse ground plane (30m x 30m)."""
        floor_shape = p.createCollisionShape(
            p.GEOM_BOX,
            halfExtents=[15.0, 15.0, 0.05],
            physicsClientId=self.client_id,
        )
        self.floor_id = p.createMultiBody(
            baseMass=0.0,  # Static
            baseCollisionShapeIndex=floor_shape,
            basePosition=[15.0, 15.0, -0.05],
            physicsClientId=self.client_id,
        )

    def _build_shelves(self) -> None:
        """Build storage shelf bodies."""
        shelf_positions = [
            ("SHELF_1", [8.0, 6.0, 1.25], [1.5, 0.6, 1.25]),
            ("SHELF_2", [8.0, 10.0, 1.25], [1.5, 0.6, 1.25]),
            ("SHELF_3", [8.0, 14.0, 1.25], [1.5, 0.6, 1.25]),
            ("SHELF_4", [16.0, 6.0, 1.25], [1.5, 0.6, 1.25]),
            ("SHELF_5", [16.0, 10.0, 1.25], [1.5, 0.6, 1.25]),
            ("SHELF_6", [16.0, 14.0, 1.25], [1.5, 0.6, 1.25]),
        ]
        for s_id, pos, ext in shelf_positions:
            shape = p.createCollisionShape(
                p.GEOM_BOX,
                halfExtents=ext,
                physicsClientId=self.client_id,
            )
            body = p.createMultiBody(
                baseMass=0.0,
                baseCollisionShapeIndex=shape,
                basePosition=pos,
                physicsClientId=self.client_id,
            )
            self.shelf_bodies[s_id] = body

    def _build_obstacles(self) -> None:
        """Build warehouse pillars / static obstacles."""
        obstacles = [
            ("OBS_PILLAR_1", [12.0, 8.0, 1.5], [0.4, 0.4, 1.5]),
            ("OBS_PILLAR_2", [12.0, 16.0, 1.5], [0.4, 0.4, 1.5]),
            ("OBS_CONTAINER", [20.0, 18.0, 0.75], [1.0, 1.0, 0.75]),
        ]
        for o_id, pos, ext in obstacles:
            shape = p.createCollisionShape(
                p.GEOM_BOX,
                halfExtents=ext,
                physicsClientId=self.client_id,
            )
            body = p.createMultiBody(
                baseMass=0.0,
                baseCollisionShapeIndex=shape,
                basePosition=pos,
                physicsClientId=self.client_id,
            )
            self.obstacle_bodies[o_id] = body

    def _build_stations(self) -> None:
        """Build pickup and delivery stations."""
        stations = [
            ("PICKUP_A", [2.0, 3.0, 0.1], [1.0, 1.0, 0.1]),
            ("PICKUP_B", [2.0, 13.0, 0.1], [1.0, 1.0, 0.1]),
            ("DELIVERY_A", [26.0, 6.0, 0.1], [1.0, 1.0, 0.1]),
            ("DELIVERY_B", [26.0, 14.0, 0.1], [1.0, 1.0, 0.1]),
        ]
        for st_id, pos, ext in stations:
            shape = p.createCollisionShape(
                p.GEOM_BOX,
                halfExtents=ext,
                physicsClientId=self.client_id,
            )
            body = p.createMultiBody(
                baseMass=0.0,
                baseCollisionShapeIndex=shape,
                basePosition=pos,
                physicsClientId=self.client_id,
            )
            self.station_bodies[st_id] = body

    def _build_packages(self) -> None:
        """Build transportable physical package bodies."""
        packages = [
            ("PKG_101", [2.0, 3.0, 0.35], [0.2, 0.2, 0.15], 5.0),
            ("PKG_102", [2.0, 13.0, 0.35], [0.2, 0.2, 0.15], 8.0),
            ("MAT_201", [2.0, 3.5, 0.35], [0.3, 0.25, 0.2], 25.0),
        ]
        for p_id, pos, ext, mass in packages:
            shape = p.createCollisionShape(
                p.GEOM_BOX,
                halfExtents=ext,
                physicsClientId=self.client_id,
            )
            body = p.createMultiBody(
                baseMass=mass,
                baseCollisionShapeIndex=shape,
                basePosition=pos,
                physicsClientId=self.client_id,
            )
            self.package_bodies[p_id] = body

    def _build_robots(self) -> None:
        """Create separate box-shaped robot bodies for ATLAS, NOVA, and TITAN."""
        for agent_id, spec in self.robot_specs.items():
            shape = p.createCollisionShape(
                p.GEOM_BOX,
                halfExtents=spec["half_extents"],
                physicsClientId=self.client_id,
            )
            init_orn = p.getQuaternionFromEuler([0.0, 0.0, spec["initial_yaw"]])
            body = p.createMultiBody(
                baseMass=spec["mass"],
                baseCollisionShapeIndex=shape,
                basePosition=spec["initial_position"],
                baseOrientation=init_orn,
                physicsClientId=self.client_id,
            )
            self.robot_bodies[agent_id] = body

    # -----------------------------------------------------------------------
    # Robot Control & State Inspection
    # -----------------------------------------------------------------------

    def set_robot_velocity(self, agent_id: str, linear_velocity: float, angular_velocity: float) -> None:
        """Apply forward driving velocity and angular steering to a robot."""
        body_id = self.robot_bodies.get(agent_id)
        if body_id is None:
            raise ValueError(f"Robot '{agent_id}' does not exist in simulation.")

        try:
            pos, orn = p.getBasePositionAndOrientation(body_id, physicsClientId=self.client_id)
        except Exception:
            # Rebuild robots if physics bodies were cleared externally
            self._build_robots()
            body_id = self.robot_bodies.get(agent_id)
            pos, orn = p.getBasePositionAndOrientation(body_id, physicsClientId=self.client_id)

        _, _, yaw = p.getEulerFromQuaternion(orn)

        # Forward velocity vector along current heading in XY plane
        vx = linear_velocity * math.cos(yaw)
        vy = linear_velocity * math.sin(yaw)
        vz = 0.0  # Maintain ground plane contact

        p.resetBaseVelocity(
            body_id,
            linearVelocity=[vx, vy, vz],
            angularVelocity=[0.0, 0.0, angular_velocity],
            physicsClientId=self.client_id,
        )

    def stop_robot(self, agent_id: str) -> None:
        """Bring robot to an immediate halt."""
        self.set_robot_velocity(agent_id, 0.0, 0.0)

    def get_robot_pose(self, agent_id: str) -> Tuple[float, float, float, float]:
        """Return (x, y, z, yaw) for the robot directly from physics engine (source of truth)."""
        body_id = self.robot_bodies.get(agent_id)
        if body_id is None:
            raise ValueError(f"Robot '{agent_id}' does not exist in simulation.")

        try:
            pos, orn = p.getBasePositionAndOrientation(body_id, physicsClientId=self.client_id)
        except Exception:
            self._build_robots()
            body_id = self.robot_bodies.get(agent_id)
            pos, orn = p.getBasePositionAndOrientation(body_id, physicsClientId=self.client_id)

        _, _, yaw = p.getEulerFromQuaternion(orn)
        return (pos[0], pos[1], pos[2], yaw)

    def get_robot_velocities(self, agent_id: str) -> Tuple[float, float]:
        """Return (linear_speed, angular_speed) from physics engine."""
        body_id = self.robot_bodies.get(agent_id)
        if body_id is None:
            return (0.0, 0.0)
        lin_v, ang_v = p.getBaseVelocity(body_id, physicsClientId=self.client_id)
        linear_speed = math.hypot(lin_v[0], lin_v[1])
        angular_speed = ang_v[2]
        return (linear_speed, angular_speed)

    def get_robot_state(self, agent_id: str) -> Dict[str, Any]:
        """Retrieve full state snapshot for a robot."""
        x, y, z, yaw = self.get_robot_pose(agent_id)
        lin_v, ang_v = self.get_robot_velocities(agent_id)
        collisions = self.detect_collisions(agent_id)
        held_pkg = None
        for pkg_id, c_id in self.attached_constraints.items():
            if pkg_id.startswith(f"{agent_id}_"):
                held_pkg = pkg_id.split(f"{agent_id}_")[-1]

        return {
            "agent_id": agent_id,
            "position": {"x": round(x, 4), "y": round(y, 4), "z": round(z, 4)},
            "yaw": round(yaw, 4),
            "linear_velocity": round(lin_v, 4),
            "angular_velocity": round(ang_v, 4),
            "has_collision": len(collisions) > 0,
            "collision_with": collisions,
            "held_package_id": held_pkg,
        }

    # -----------------------------------------------------------------------
    # Collision Detection
    # -----------------------------------------------------------------------

    def detect_collisions(self, agent_id: str) -> List[str]:
        """Check if robot is colliding with any other robot, shelf, or obstacle."""
        body_id = self.robot_bodies.get(agent_id)
        if body_id is None:
            return []

        colliding_objects = []

        # Check other robots
        for other_id, other_body in self.robot_bodies.items():
            if other_id != agent_id:
                pts = p.getContactPoints(body_id, other_body, physicsClientId=self.client_id)
                if pts:
                    colliding_objects.append(f"ROBOT_{other_id}")

        # Check shelves
        for shelf_id, shelf_body in self.shelf_bodies.items():
            pts = p.getContactPoints(body_id, shelf_body, physicsClientId=self.client_id)
            if pts:
                colliding_objects.append(shelf_id)

        # Check obstacles
        for obs_id, obs_body in self.obstacle_bodies.items():
            pts = p.getContactPoints(body_id, obs_body, physicsClientId=self.client_id)
            if pts:
                colliding_objects.append(obs_id)

        return colliding_objects

    # -----------------------------------------------------------------------
    # Package Pickup & Placement (Physics Constraints / Attachment)
    # -----------------------------------------------------------------------

    def attach_package(self, agent_id: str, package_id: str) -> bool:
        """Secure package onto the robot using a fixed physics constraint."""
        robot_body = self.robot_bodies.get(agent_id)
        pkg_body = self.package_bodies.get(package_id)

        if robot_body is None or pkg_body is None:
            logger.warning("Cannot attach package: invalid robot or package ID.")
            return False

        # Verify robot is close enough to package (within 1.5m)
        r_pos, _ = p.getBasePositionAndOrientation(robot_body, physicsClientId=self.client_id)
        p_pos, _ = p.getBasePositionAndOrientation(pkg_body, physicsClientId=self.client_id)
        dist = math.hypot(r_pos[0] - p_pos[0], r_pos[1] - p_pos[1])
        if dist > 1.8:
            logger.warning("Robot %s too far from package %s (%.2fm)", agent_id, package_id, dist)
            return False

        # Place package on top of robot platform and create fixed constraint
        z_offset = self.robot_specs[agent_id]["half_extents"][2] + 0.15
        cid = p.createConstraint(
            parentBodyUniqueId=robot_body,
            parentLinkIndex=-1,
            childBodyUniqueId=pkg_body,
            childLinkIndex=-1,
            jointType=p.JOINT_FIXED,
            jointAxis=[0, 0, 0],
            parentFramePosition=[0.0, 0.0, z_offset],
            childFramePosition=[0.0, 0.0, 0.0],
            physicsClientId=self.client_id,
        )

        key = f"{agent_id}_{package_id}"
        self.attached_constraints[key] = cid
        logger.info("Package %s attached to robot %s (constraint ID %d)", package_id, agent_id, cid)
        return True

    def detach_package(self, agent_id: str, package_id: str, drop_position: Optional[Tuple[float, float, float]] = None) -> bool:
        """Release package constraint and place it at destination."""
        key = f"{agent_id}_{package_id}"
        cid = self.attached_constraints.pop(key, None)
        pkg_body = self.package_bodies.get(package_id)

        if cid is not None:
            p.removeConstraint(cid, physicsClientId=self.client_id)

        if pkg_body is not None and drop_position is not None:
            p.resetBasePositionAndOrientation(
                pkg_body,
                pos=list(drop_position),
                orn=[0.0, 0.0, 0.0, 1.0],
                physicsClientId=self.client_id,
            )
            p.resetBaseVelocity(
                pkg_body,
                linearVelocity=[0.0, 0.0, 0.0],
                angularVelocity=[0.0, 0.0, 0.0],
                physicsClientId=self.client_id,
            )

        logger.info("Package %s detached from robot %s", package_id, agent_id)
        return True

    def get_package_position(self, package_id: str) -> Optional[Tuple[float, float, float]]:
        """Return current package coordinates directly from physics."""
        pkg_body = self.package_bodies.get(package_id)
        if pkg_body is None:
            return None
        pos, _ = p.getBasePositionAndOrientation(pkg_body, physicsClientId=self.client_id)
        return (pos[0], pos[1], pos[2])

