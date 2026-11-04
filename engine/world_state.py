"""RoboTrace 3D — World State Definitions.

Defines spatial representations, warehouse fixtures (shelves, stations, obstacles),
packages, inventory data models, and world state snapshot utilities.
Z-up coordinate system is used throughout.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ObjectType(str, Enum):
    """Types of physical warehouse entities."""
    FLOOR = "floor"
    SHELF = "shelf"
    OBSTACLE = "obstacle"
    PICKUP_STATION = "pickup_station"
    DELIVERY_STATION = "delivery_station"
    PACKAGE = "package"
    ROBOT = "robot"


@dataclass
class Pose3D:
    """Rigid body 3D pose in Z-up coordinates.

    Yaw is in radians about the +Z axis:
    0 = facing +X, pi/2 = facing +Y, pi = facing -X, -pi/2 = facing -Y.
    """
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0

    def as_tuple(self) -> Tuple[float, float, float]:
        """Return (x, y, z) position tuple."""
        return (self.x, self.y, self.z)

    def as_dict(self) -> Dict[str, float]:
        """Return dictionary representation."""
        return {
            "x": round(self.x, 4),
            "y": round(self.y, 4),
            "z": round(self.z, 4),
            "yaw": round(self.yaw, 4),
        }


@dataclass
class BoundingBox:
    """Axis-aligned bounding box for spatial and collision queries."""
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float
    max_z: float

    def contains(self, x: float, y: float, z: float) -> bool:
        """Check if point is inside bounding box."""
        return (
            self.min_x <= x <= self.max_x
            and self.min_y <= y <= self.max_y
            and self.min_z <= z <= self.max_z
        )

    def intersects(self, other: "BoundingBox", margin: float = 0.0) -> bool:
        """Check intersection with another bounding box."""
        return not (
            self.max_x + margin < other.min_x
            or self.min_x - margin > other.max_x
            or self.max_y + margin < other.min_y
            or self.min_y - margin > other.max_y
            or self.max_z + margin < other.min_z
            or self.min_z - margin > other.max_z
        )


@dataclass
class WarehouseFixture:
    """A static object in the warehouse (shelf, pillar obstacle, station)."""
    id: str
    object_type: ObjectType
    name: str
    position: Tuple[float, float, float]
    dimensions: Tuple[float, float, float]  # (length_x, width_y, height_z)
    body_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def bounding_box(self) -> BoundingBox:
        """Compute axis-aligned bounding box from center and dimensions."""
        px, py, pz = self.position
        dx, dy, dz = self.dimensions
        return BoundingBox(
            min_x=px - dx / 2.0,
            max_x=px + dx / 2.0,
            min_y=py - dy / 2.0,
            max_y=py + dy / 2.0,
            min_z=pz - dz / 2.0,
            max_z=pz + dz / 2.0,
        )


@dataclass
class ShelfData:
    """A storage shelf holding categorized inventory."""
    id: str
    name: str
    position: Tuple[float, float, float]
    dimensions: Tuple[float, float, float]
    items: Dict[str, int] = field(default_factory=dict)
    expected_inventory: Dict[str, int] = field(default_factory=dict)
    body_id: Optional[int] = None


@dataclass
class StationData:
    """Pickup or delivery station."""
    id: str
    name: str
    station_type: ObjectType  # PICKUP_STATION or DELIVERY_STATION
    position: Tuple[float, float, float]
    dimensions: Tuple[float, float, float]
    accepted_agent_ids: List[str] = field(default_factory=list)
    body_id: Optional[int] = None


@dataclass
class PackageData:
    """A transportable package or material item."""
    id: str
    name: str
    position: Tuple[float, float, float]
    destination_station_id: str
    weight: float = 5.0
    dimensions: Tuple[float, float, float] = (0.4, 0.4, 0.4)
    body_id: Optional[int] = None
    held_by_agent_id: Optional[str] = None
    delivered: bool = False
    verified: bool = False


@dataclass
class RobotState:
    """Current state of a mobile robot extracted from simulation."""
    agent_id: str
    body_id: int
    pose: Pose3D
    linear_velocity: float = 0.0
    angular_velocity: float = 0.0
    held_package_id: Optional[str] = None
    has_collision: bool = False
    collision_with: List[str] = field(default_factory=list)


class WorldState:
    """Central container maintaining warehouse state."""

    def __init__(self, width: float = 30.0, length: float = 30.0, height: float = 6.0):
        self.width = width      # X extent
        self.length = length    # Y extent
        self.height = height    # Z extent
        self.shelves: Dict[str, ShelfData] = {}
        self.stations: Dict[str, StationData] = {}
        self.obstacles: Dict[str, WarehouseFixture] = {}
        self.packages: Dict[str, PackageData] = {}
        self.robots: Dict[str, RobotState] = {}

    def get_station_position(self, station_id: str) -> Optional[Tuple[float, float, float]]:
        """Return position of station by ID."""
        station = self.stations.get(station_id)
        return station.position if station else None

    def get_shelf(self, shelf_id: str) -> Optional[ShelfData]:
        """Return shelf data by ID."""
        return self.shelves.get(shelf_id)

    def get_package(self, package_id: str) -> Optional[PackageData]:
        """Return package data by ID."""
        return self.packages.get(package_id)

    def get_obstacles_bounding_boxes(self) -> List[BoundingBox]:
        """Return bounding boxes of all non-traversable fixtures."""
        boxes = []
        for shelf in self.shelves.values():
            px, py, pz = shelf.position
            dx, dy, dz = shelf.dimensions
            boxes.append(BoundingBox(
                min_x=px - dx / 2.0, max_x=px + dx / 2.0,
                min_y=py - dy / 2.0, max_y=py + dy / 2.0,
                min_z=0.0, max_z=pz + dz / 2.0,
            ))
        for obs in self.obstacles.values():
            boxes.append(obs.bounding_box)
        return boxes

