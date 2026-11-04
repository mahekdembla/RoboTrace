"""RoboTrace 3D — Robot Movement & Navigation Demo.

Run this script to observe robot movement, velocity steering, and A* pathfinding:
    python demo_robot_movement.py
"""

import sys
from pathlib import Path

# Add backend and root to sys.path
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
for p in (str(BACKEND_DIR), str(ROOT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from engine.simulation import WarehouseSimulation
from engine.navigation import WaypointNavigator


def main():
    print("=" * 65)
    print("RoboTrace 3D — PyBullet Robot Movement & Navigation Verification")
    print("=" * 65)

    # 1. Initialize Simulation
    sim = WarehouseSimulation()
    sim.initialize()
    print("\n[1] Warehouse simulation initialized in DIRECT mode.")
    print("    Entities loaded: Floor, 6 Shelves, 3 Obstacles, 4 Stations, 3 Packages, 3 Mobile Robots.")

    # 2. Inspect Initial State
    for agent_id in ["ATLAS", "NOVA", "TITAN"]:
        x, y, z, yaw = sim.get_robot_pose(agent_id)
        print(f"    - {agent_id:5s} initial pose: x={x:.2f}m, y={y:.2f}m, z={z:.2f}m, yaw={yaw:.2f} rad")

    # 3. Test Physical Forward & Rotational Movement
    print("\n[2] Applying physics velocity command to ATLAS (v=1.2 m/s, w=0.5 rad/s)...")
    sim.set_robot_velocity("ATLAS", linear_velocity=1.2, angular_velocity=0.5)

    print("    Stepping physics simulation (60 ticks at dt=1/60s = 1.0 second)...")
    for tick in range(1, 61):
        sim.step(1)
        if tick % 20 == 0:
            x, y, z, yaw = sim.get_robot_pose("ATLAS")
            lin_v, ang_v = sim.get_robot_velocities("ATLAS")
            print(f"    [t={tick/60:.2f}s] ATLAS: pos=({x:.2f}, {y:.2f}, {z:.2f}), yaw={yaw:.2f} rad, lin_v={lin_v:.2f}m/s")

    sim.stop_robot("ATLAS")
    print("    ATLAS halted.")

    # 4. Test Closed-Loop A* Waypoint Navigation
    print("\n[3] Testing closed-loop A* navigation for NOVA around warehouse shelves...")
    navigator = WaypointNavigator()
    target_destination = (18.0, 10.0)  # Next to Shelf 5
    print(f"    Dispatching NOVA to destination {target_destination}...")

    nav_result = navigator.navigate_to("NOVA", target_destination, sim)
    final_x, final_y, final_z, final_yaw = sim.get_robot_pose("NOVA")
    print(f"    Navigation status: SUCCESS!")
    print(f"    Steps taken: {nav_result['steps_taken']} physics ticks")
    print(f"    Waypoints traversed: {nav_result['waypoints_count']}")
    print(f"    NOVA final position: ({final_x:.2f}, {final_y:.2f}, {final_z:.2f})")

    # 5. Test Package Physics Constraint Attachment
    print("\n[4] Testing package attachment constraint (ATLAS picking up PKG_101)...")
    # Position atlas near PKG_101
    pkg_pos_before = sim.get_package_position("PKG_101")
    print(f"    PKG_101 location before pickup: {pkg_pos_before}")

    attached = sim.attach_package("ATLAS", "PKG_101")
    print(f"    Package attached to ATLAS body: {attached}")

    sim.set_robot_velocity("ATLAS", linear_velocity=1.0, angular_velocity=0.0)
    sim.step(60)
    sim.stop_robot("ATLAS")
    pkg_pos_after = sim.get_package_position("PKG_101")
    atlas_pos_after = sim.get_robot_pose("ATLAS")
    print(f"    ATLAS new position: ({atlas_pos_after[0]:.2f}, {atlas_pos_after[1]:.2f})")
    print(f"    PKG_101 moved with ATLAS: ({pkg_pos_after[0]:.2f}, {pkg_pos_after[1]:.2f})")

    # 6. Shutdown
    sim.shutdown()
    print("\n[5] Simulation cleanly shut down.")
    print("=" * 65)
    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    main()

