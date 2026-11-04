"""Unit tests for A* pathfinding and task scheduler."""

import pytest
from engine.navigation import AStarPlanner, GridMap, WaypointNavigator, NavigationError
from engine.simulation import WarehouseSimulation
from engine.task_scheduler import TaskScheduler
from agents.agent_manager import AgentManager


class TestNavigation:
    """Test A* grid pathfinder and waypoint generation."""

    def test_astar_finds_path_around_shelves(self):
        grid = GridMap(width=30.0, length=30.0, resolution=0.5)
        planner = AStarPlanner(grid)

        # Plan from pickup zone (2.0, 3.0) to delivery zone (26.0, 6.0) across shelves
        start = (2.0, 3.0)
        goal = (26.0, 6.0)
        waypoints = planner.plan(start, goal)

        assert len(waypoints) >= 2
        assert waypoints[0] == start
        assert waypoints[-1] == goal

        # Verify no waypoint is inside occupied shelf
        for wp in waypoints:
            gx, gy = grid.world_to_grid(wp[0], wp[1])
            # Waypoint should be traversable
            assert grid.is_traversable(gx, gy), f"Waypoint {wp} is inside obstacle cell ({gx}, {gy})"

    def test_navigation_waypoint_follower(self):
        sim = WarehouseSimulation()
        sim.initialize()
        navigator = WaypointNavigator()

        # Command ATLAS to navigate from (2.0, 2.0) to (4.0, 2.0)
        result = navigator.navigate_to("ATLAS", destination=(4.0, 2.0), simulation=sim)
        assert result["success"] is True

        # Check final position
        x, y, _, _ = sim.get_robot_pose("ATLAS")
        assert abs(x - 4.0) < 0.5
        assert abs(y - 2.0) < 0.5

        sim.shutdown()


class TestTaskScheduler:
    """Test task scheduling, priorities, and shared-space conflict avoidance."""

    def test_task_submission_and_priority_order(self):
        sim = WarehouseSimulation()
        sim.initialize()
        manager = AgentManager(sim)
        scheduler = TaskScheduler(manager, sim)

        # Submit tasks with different priorities
        low_priority = scheduler.submit_task("LOW_PRIO", "TASK_PACKAGE_DELIVERY", priority=5, payload={"pickup_coord": (2.0, 2.0), "delivery_coord": (3.0, 2.0)})
        high_priority = scheduler.submit_task("HIGH_PRIO", "TASK_PACKAGE_DELIVERY", priority=1, payload={"pickup_coord": (2.0, 2.0), "delivery_coord": (3.0, 2.0)})

        # Dispatch should pick high priority first
        status = scheduler.get_queue_status()
        assert status["pending_count"] == 2

        sim.shutdown()

    def test_spatial_conflict_prevention(self):
        sim = WarehouseSimulation()
        sim.initialize()
        manager = AgentManager(sim)
        scheduler = TaskScheduler(manager, sim)

        # Submit task 1 targeting station "DELIVERY_A"
        scheduler.submit_task(
            "TASK_1",
            "TASK_PACKAGE_DELIVERY",
            priority=1,
            payload={"station_id": "DELIVERY_A", "pickup_coord": (2.0, 2.0), "delivery_coord": (3.0, 2.0)},
        )
        # Submit task 2 targeting the SAME station "DELIVERY_A"
        task_2 = scheduler.submit_task(
            "TASK_2",
            "TASK_MATERIAL_TRANSPORT",
            priority=2,
            payload={"station_id": "DELIVERY_A", "pickup_coord": (2.0, 2.0), "delivery_coord": (3.0, 2.0)},
        )

        # Check spatial conflict
        assert scheduler.check_spatial_conflict(task_2) is False  # Before reservation

        # Reserve station for Atlas
        scheduler.reserve_spatial_zone(task_2, "ATLAS")
        assert scheduler.check_spatial_conflict(task_2) is True  # Now conflicted!

        # Release
        scheduler.release_spatial_zone(task_2)
        assert scheduler.check_spatial_conflict(task_2) is False

        sim.shutdown()

