"""RoboTrace 3D — Grid-Based A* Pathfinding and Waypoint Navigation.

Provides:
- 2D grid occupancy map generated from warehouse static geometry.
- A* pathfinder avoiding shelves and static obstacles.
- Waypoint extraction and trajectory path following.
- Real-time closed-loop steering and forward movement commanded to PyBullet simulation.
- Dynamic route blockage detection and navigation failure handling.
"""

import heapq
import math
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from engine.simulation import WarehouseSimulation
from engine.world_state import BoundingBox

logger = logging.getLogger("robotrace.navigation")


class NavigationError(Exception):
    """Raised when pathfinding fails or a robot's path is blocked."""
    pass


class GridMap:
    """Discretized 2D occupancy grid representing traversable warehouse floor."""

    def __init__(
        self,
        width: float = 30.0,
        length: float = 30.0,
        resolution: float = 0.5,
        safety_margin: float = 0.4,
    ):
        self.width = width
        self.length = length
        self.resolution = resolution
        self.safety_margin = safety_margin

        self.cols = int(math.ceil(width / resolution))
        self.rows = int(math.ceil(length / resolution))

        # 0 = free, 1 = occupied
        self.grid: List[List[int]] = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self._populate_default_obstacles()

    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """Convert continuous (x, y) coordinates to discrete (grid_x, grid_y)."""
        gx = int(x / self.resolution)
        gy = int(y / self.resolution)
        gx = max(0, min(self.cols - 1, gx))
        gy = max(0, min(self.rows - 1, gy))
        return (gx, gy)

    def grid_to_world(self, gx: int, gy: int) -> Tuple[float, float]:
        """Convert discrete (grid_x, grid_y) to continuous center (x, y)."""
        x = (gx + 0.5) * self.resolution
        y = (gy + 0.5) * self.resolution
        return (x, y)

    def is_traversable(self, gx: int, gy: int) -> bool:
        """Check if grid cell is within bounds and free."""
        if 0 <= gx < self.cols and 0 <= gy < self.rows:
            return self.grid[gy][gx] == 0
        return False

    def mark_occupied_box(self, box: BoundingBox) -> None:
        """Mark cells covered by a bounding box plus safety margin as occupied."""
        min_gx, min_gy = self.world_to_grid(box.min_x - self.safety_margin, box.min_y - self.safety_margin)
        max_gx, max_gy = self.world_to_grid(box.max_x + self.safety_margin, box.max_y + self.safety_margin)

        for r in range(min_gy, max_gy + 1):
            for c in range(min_gx, max_gx + 1):
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    self.grid[r][c] = 1

    def _populate_default_obstacles(self) -> None:
        """Populate grid with static warehouse shelf and obstacle layouts."""
        # Shelves layout (6 shelves)
        shelf_boxes = [
            BoundingBox(8.0 - 1.5, 8.0 + 1.5, 6.0 - 0.6, 6.0 + 0.6, 0.0, 2.5),
            BoundingBox(8.0 - 1.5, 8.0 + 1.5, 10.0 - 0.6, 10.0 + 0.6, 0.0, 2.5),
            BoundingBox(8.0 - 1.5, 8.0 + 1.5, 14.0 - 0.6, 14.0 + 0.6, 0.0, 2.5),
            BoundingBox(16.0 - 1.5, 16.0 + 1.5, 6.0 - 0.6, 6.0 + 0.6, 0.0, 2.5),
            BoundingBox(16.0 - 1.5, 16.0 + 1.5, 10.0 - 0.6, 10.0 + 0.6, 0.0, 2.5),
            BoundingBox(16.0 - 1.5, 16.0 + 1.5, 14.0 - 0.6, 14.0 + 0.6, 0.0, 2.5),
        ]
        # Obstacles (pillars & container)
        obstacle_boxes = [
            BoundingBox(12.0 - 0.4, 12.0 + 0.4, 8.0 - 0.4, 8.0 + 0.4, 0.0, 3.0),
            BoundingBox(12.0 - 0.4, 12.0 + 0.4, 16.0 - 0.4, 16.0 + 0.4, 0.0, 3.0),
            BoundingBox(20.0 - 1.0, 20.0 + 1.0, 18.0 - 1.0, 18.0 + 1.0, 0.0, 1.5),
        ]

        for box in shelf_boxes + obstacle_boxes:
            self.mark_occupied_box(box)


class AStarPlanner:
    """A* pathfinding on 2D occupancy grid with diagonal movement."""

    # 8-connected grid offsets and movement costs
    MOTIONS: List[Tuple[int, int, float]] = [
        (1, 0, 1.0),
        (-1, 0, 1.0),
        (0, 1, 1.0),
        (0, -1, 1.0),
        (1, 1, 1.4142),
        (-1, 1, 1.4142),
        (1, -1, 1.4142),
        (-1, -1, 1.4142),
    ]

    def __init__(self, grid_map: GridMap):
        self.grid_map = grid_map

    @staticmethod
    def _heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Euclidean distance heuristic."""
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def plan(self, start: Tuple[float, float], goal: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Compute shortest collision-free waypoint path from start to goal coordinates."""
        start_cell = self.grid_map.world_to_grid(start[0], start[1])
        goal_cell = self.grid_map.world_to_grid(goal[0], goal[1])

        if not self.grid_map.is_traversable(start_cell[0], start_cell[1]):
            logger.warning("Start cell %s is inside an obstacle.", start_cell)
            start_cell = self._find_nearest_free_cell(start_cell)

        if not self.grid_map.is_traversable(goal_cell[0], goal_cell[1]):
            logger.warning("Goal cell %s is inside an obstacle. Finding adjacent free cell.", goal_cell)
            goal_cell = self._find_nearest_free_cell(goal_cell)

        # Priority queue entries: (f_score, counter, current_cell)
        counter = 0
        open_set: List[Tuple[float, int, Tuple[int, int]]] = []
        heapq.heappush(open_set, (0.0, counter, start_cell))

        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_score: Dict[Tuple[int, int], float] = {start_cell: 0.0}
        closed_set: Set[Tuple[int, int]] = set()

        while open_set:
            _, _, current = heapq.heappop(open_set)

            if current == goal_cell:
                return self._reconstruct_path(came_from, current, start, goal)

            if current in closed_set:
                continue
            closed_set.add(current)

            for dx, dy, cost in self.MOTIONS:
                neighbor = (current[0] + dx, current[1] + dy)

                if neighbor in closed_set or not self.grid_map.is_traversable(neighbor[0], neighbor[1]):
                    continue

                # Prevent diagonal corner cutting
                if dx != 0 and dy != 0:
                    if not self.grid_map.is_traversable(current[0] + dx, current[1]) or \
                       not self.grid_map.is_traversable(current[0], current[1] + dy):
                        continue

                tentative_g = g_score[current] + cost
                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self._heuristic(neighbor, goal_cell)
                    counter += 1
                    heapq.heappush(open_set, (f_score, counter, neighbor))

        raise NavigationError(f"No collision-free path found between {start} and {goal}.")

    def _find_nearest_free_cell(self, cell: Tuple[int, int]) -> Tuple[int, int]:
        """Breadth-first search for the nearest traversable cell."""
        queue = [cell]
        visited = {cell}
        while queue:
            curr = queue.pop(0)
            if self.grid_map.is_traversable(curr[0], curr[1]):
                return curr
            for dx, dy, _ in self.MOTIONS:
                nxt = (curr[0] + dx, curr[1] + dy)
                if 0 <= nxt[0] < self.grid_map.cols and 0 <= nxt[1] < self.grid_map.rows and nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
        return cell

    def _reconstruct_path(
        self,
        came_from: Dict[Tuple[int, int], Tuple[int, int]],
        current: Tuple[int, int],
        exact_start: Tuple[float, float],
        exact_goal: Tuple[float, float],
    ) -> List[Tuple[float, float]]:
        """Reconstruct waypoints from search tree and simplify collinear points."""
        path_cells = [current]
        while current in came_from:
            current = came_from[current]
            path_cells.append(current)
        path_cells.reverse()

        # Convert to world coordinates
        waypoints = [exact_start]
        for cell in path_cells[1:-1]:
            waypoints.append(self.grid_map.grid_to_world(cell[0], cell[1]))
        waypoints.append(exact_goal)

        return self._simplify_waypoints(waypoints)

    @staticmethod
    def _simplify_waypoints(waypoints: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Remove intermediate points along straight collinear segments."""
        if len(waypoints) <= 2:
            return waypoints

        simplified = [waypoints[0]]
        for i in range(1, len(waypoints) - 1):
            p_prev = simplified[-1]
            p_curr = waypoints[i]
            p_next = waypoints[i + 1]

            # Vector cross product to test collinearity
            dx1, dy1 = p_curr[0] - p_prev[0], p_curr[1] - p_prev[1]
            dx2, dy2 = p_next[0] - p_curr[0], p_next[1] - p_curr[1]
            cross = abs(dx1 * dy2 - dy1 * dx2)

            if cross > 1e-4:
                simplified.append(p_curr)

        simplified.append(waypoints[-1])
        return simplified


class WaypointNavigator:
    """Follows waypoints using closed-loop proportional steering and forward thrust."""

    def __init__(self, grid_map: Optional[GridMap] = None):
        self.grid_map = grid_map or GridMap()
        self.planner = AStarPlanner(self.grid_map)

    def navigate_to(
        self,
        agent_id: str,
        destination: Tuple[float, float],
        simulation: WarehouseSimulation,
        max_speed: float = 1.2,
        arrival_threshold: float = 0.35,
        max_simulation_steps: int = 2000,
    ) -> Dict[str, Any]:
        """Navigate robot to destination by issuing physical velocity commands.

        Advances simulation in discrete steps, checks collisions, and tracks progress.
        """
        start_x, start_y, _, _ = simulation.get_robot_pose(agent_id)
        start = (start_x, start_y)

        # Plan waypoints using A*
        waypoints = self.planner.plan(start, destination)
        logger.info("Agent %s planned %d waypoints to %s", agent_id, len(waypoints), destination)

        trajectory_log: List[Dict[str, float]] = []
        current_wp_idx = 0
        step_count = 0

        while current_wp_idx < len(waypoints) and step_count < max_simulation_steps:
            target_wp = waypoints[current_wp_idx]
            cur_x, cur_y, cur_z, cur_yaw = simulation.get_robot_pose(agent_id)

            # Record spatial trace
            trajectory_log.append({
                "x": round(cur_x, 4),
                "y": round(cur_y, 4),
                "z": round(cur_z, 4),
                "yaw": round(cur_yaw, 4),
            })

            # Check distance to target waypoint
            dist = math.hypot(target_wp[0] - cur_x, target_wp[1] - cur_y)
            if dist <= arrival_threshold:
                current_wp_idx += 1
                if current_wp_idx >= len(waypoints):
                    break
                target_wp = waypoints[current_wp_idx]

            # Compute steering heading towards target
            desired_yaw = math.atan2(target_wp[1] - cur_y, target_wp[0] - cur_x)
            yaw_error = desired_yaw - cur_yaw
            # Normalize yaw error to [-pi, pi]
            yaw_error = (yaw_error + math.pi) % (2 * math.pi) - math.pi

            # Proportional angular controller
            angular_velocity = max(-2.5, min(2.5, 3.0 * yaw_error))

            # Forward speed modulated by alignment
            if abs(yaw_error) < 0.6:
                linear_velocity = max(0.2, min(max_speed, 1.5 * dist))
            else:
                linear_velocity = 0.1  # Rotate in place when significantly misaligned

            # Apply physical velocity commands to simulation
            simulation.set_robot_velocity(agent_id, linear_velocity, angular_velocity)
            simulation.step(1)
            step_count += 1

            # Collision check
            collisions = simulation.detect_collisions(agent_id)
            if collisions:
                simulation.stop_robot(agent_id)
                raise NavigationError(
                    f"Agent {agent_id} detected collision with {collisions} at position ({cur_x:.2f}, {cur_y:.2f})."
                )

        simulation.stop_robot(agent_id)

        final_x, final_y, final_z, final_yaw = simulation.get_robot_pose(agent_id)
        final_dist = math.hypot(destination[0] - final_x, destination[1] - final_y)

        if final_dist > (arrival_threshold + 0.3):
            raise NavigationError(
                f"Agent {agent_id} failed to reach {destination} within {max_simulation_steps} steps (remaining dist: {final_dist:.2f}m)."
            )

        return {
            "success": True,
            "agent_id": agent_id,
            "steps_taken": step_count,
            "final_position": (round(final_x, 4), round(final_y, 4), round(final_z, 4)),
            "waypoints_count": len(waypoints),
            "trajectory_points": len(trajectory_log),
        }

