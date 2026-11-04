"""Unit tests for RoboTrace 3D PyBullet Warehouse Simulation."""

import pytest
from engine.simulation import WarehouseSimulation


class TestWarehouseSimulation:
    """Test warehouse world construction, physics advancement, and robot control."""

    def test_initialize_warehouse_and_create_robots(self):
        sim = WarehouseSimulation()
        sim.initialize()

        assert sim._is_initialized is True
        assert sim.client_id is not None

        # Verify all 3 robot bodies created
        assert "ATLAS" in sim.robot_bodies
        assert "NOVA" in sim.robot_bodies
        assert "TITAN" in sim.robot_bodies

        # Verify warehouse fixtures
        assert len(sim.shelf_bodies) == 6
        assert len(sim.obstacle_bodies) >= 3
        assert len(sim.station_bodies) == 4
        assert len(sim.package_bodies) >= 3

        sim.shutdown()

    def test_prevent_duplicate_physics_connections(self):
        sim = WarehouseSimulation()
        sim.initialize()

        # Calling initialize again should not crash or create duplicate leak
        sim.initialize()
        assert sim._is_initialized is True

        sim.shutdown()

    def test_advance_physics_simulation(self):
        sim = WarehouseSimulation()
        sim.initialize()

        # Advance physics simulation steps
        sim.step(10)
        sim.step(50)

        # Retrieve robot pose directly from simulation
        x, y, z, yaw = sim.get_robot_pose("ATLAS")
        assert isinstance(x, float)
        assert isinstance(y, float)
        assert isinstance(z, float)
        assert z >= 0.0  # Above ground

        sim.shutdown()

    def test_robot_forward_and_rotational_movement(self):
        sim = WarehouseSimulation()
        sim.initialize()

        x0, y0, z0, yaw0 = sim.get_robot_pose("ATLAS")

        # Command forward velocity
        sim.set_robot_velocity("ATLAS", linear_velocity=1.0, angular_velocity=0.0)

        # Advance physics simulation steps
        sim.step(60)

        x1, y1, z1, yaw1 = sim.get_robot_pose("ATLAS")

        # Position should have physically advanced along heading (x increases for yaw=0)
        assert x1 > x0, f"Robot did not move forward physically: x0={x0}, x1={x1}"

        # Command rotation
        sim.set_robot_velocity("ATLAS", linear_velocity=0.0, angular_velocity=1.5)
        sim.step(30)
        _, _, _, yaw2 = sim.get_robot_pose("ATLAS")
        assert yaw2 != yaw1, "Robot did not rotate physically."

        sim.stop_robot("ATLAS")
        lin_v, ang_v = sim.get_robot_velocities("ATLAS")
        assert lin_v == 0.0
        assert ang_v == 0.0

        sim.shutdown()

    def test_package_attachment_and_detachment(self):
        sim = WarehouseSimulation()
        sim.initialize()

        # ATLAS starts at (2.0, 2.0). Package PKG_101 is at (2.0, 3.0)
        attached = sim.attach_package("ATLAS", "PKG_101")
        assert attached is True

        # Advance physics while robot moves
        sim.set_robot_velocity("ATLAS", 1.0, 0.0)
        sim.step(30)

        # Package position should track robot position
        pkg_pos = sim.get_package_position("PKG_101")
        r_pos = sim.get_robot_pose("ATLAS")
        assert abs(pkg_pos[0] - r_pos[0]) < 0.8

        # Detach package
        detached = sim.detach_package("ATLAS", "PKG_101", drop_position=(26.0, 6.0, 0.35))
        assert detached is True
        final_pkg_pos = sim.get_package_position("PKG_101")
        assert abs(final_pkg_pos[0] - 26.0) < 0.1

        sim.shutdown()

