"""RoboTrace 3D — Real-Time Simulation WebSocket.

Provides high-frequency (approx. 10 Hz) live simulation state broadcasting:
- Broadcast message types:
    * robot_update
    * agent_status
    * task_update
    * simulation_event
    * collision_detected
    * error_detected
    * mission_completed
    * mission_failed
- Sends actual PyBullet physics coordinates (Z-up, yaw in radians).
- Supports multiple concurrent frontend connections with safe disconnect handling.
- Keeps physics simulation running even when no clients are connected.
"""

import asyncio
from datetime import datetime, timezone
import json
import logging
from typing import Any, Dict, List, Optional, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from engine.simulation import WarehouseSimulation

logger = logging.getLogger("robotrace.websocket")

router = APIRouter()


class SimulationConnectionManager:
    """Manages active WebSocket client connections and safe broadcast distribution."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.simulation: Optional[WarehouseSimulation] = None
        self._broadcast_task: Optional[asyncio.Task] = None
        self._is_broadcasting: bool = False

    async def connect(self, websocket: WebSocket) -> None:
        """Accept connection and register client."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info("WebSocket client connected. Total active: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove disconnected client."""
        self.active_connections.discard(websocket)
        logger.info("WebSocket client disconnected. Total active: %d", len(self.active_connections))

    async def broadcast_message(self, message: Dict[str, Any]) -> None:
        """Send message to all active clients safely, pruning disconnected ones."""
        if not self.active_connections:
            return

        payload = json.dumps(message)
        dead_connections = []

        for conn in list(self.active_connections):
            try:
                await conn.send_text(payload)
            except Exception:
                dead_connections.append(conn)

        for dead in dead_connections:
            self.disconnect(dead)

    def start_broadcasting(self, simulation: WarehouseSimulation) -> None:
        """Start 10 Hz background telemetry broadcast loop."""
        self.simulation = simulation
        if self._broadcast_task is None or self._broadcast_task.done():
            self._is_broadcasting = True
            self._broadcast_task = asyncio.create_task(self._broadcast_loop())
            logger.info("Started 10 Hz WebSocket telemetry broadcast loop.")

    def stop_broadcasting(self) -> None:
        """Stop background telemetry loop."""
        self._is_broadcasting = False
        if self._broadcast_task and not self._broadcast_task.done():
            self._broadcast_task.cancel()
        logger.info("Stopped WebSocket telemetry loop.")

    async def _broadcast_loop(self) -> None:
        """Background loop broadcasting robot physics states at ~10 Hz (every 100ms)."""
        while self._is_broadcasting:
            try:
                if self.simulation and self.simulation._is_initialized:
                    for agent_id in ("ATLAS", "NOVA", "TITAN"):
                        try:
                            x, y, z, yaw = self.simulation.get_robot_pose(agent_id)
                            lin_v, ang_v = self.simulation.get_robot_velocities(agent_id)
                            collisions = self.simulation.detect_collisions(agent_id)

                            robot_msg = {
                                "type": "robot_update",
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "data": {
                                    "agent_id": agent_id,
                                    "pose": {
                                        "x": round(x, 4),
                                        "y": round(y, 4),
                                        "z": round(z, 4),
                                        "yaw": round(yaw, 4),
                                    },
                                    "linear_velocity": round(lin_v, 4),
                                    "angular_velocity": round(ang_v, 4),
                                    "has_collision": len(collisions) > 0,
                                },
                            }
                            await self.broadcast_message(robot_msg)

                            if collisions:
                                col_msg = {
                                    "type": "collision_detected",
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                    "data": {
                                        "agent_id": agent_id,
                                        "colliding_objects": collisions,
                                    },
                                }
                                await self.broadcast_message(col_msg)

                        except Exception:
                            pass

                # Approximately 10 Hz
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.debug("Error in broadcast loop: %s", exc)
                await asyncio.sleep(0.1)


ws_manager = SimulationConnectionManager()


@router.websocket("/ws/simulation")
async def websocket_simulation_endpoint(websocket: WebSocket):
    """WebSocket connection endpoint for live simulation streaming."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Listen for client messages (e.g. PING, SUBSCRIBE)
            text = await websocket.receive_text()
            try:
                data = json.loads(text)
                msg_type = data.get("type", "").upper()

                if msg_type == "PING":
                    await websocket.send_text(json.dumps({
                        "type": "PONG",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }))
                elif msg_type == "SUBSCRIBE":
                    mission_id = data.get("data", {}).get("mission_id", 1)
                    await websocket.send_text(json.dumps({
                        "type": "SUBSCRIBED",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "data": {"mission_id": mission_id, "message": f"Subscribed to mission {mission_id}."},
                    }))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as exc:
        logger.debug("WebSocket client exception: %s", exc)
        ws_manager.disconnect(websocket)
