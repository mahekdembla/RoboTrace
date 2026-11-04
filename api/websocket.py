"""Top-level re-export of simulation WebSocket router."""

from backend.api.websocket import router, ws_manager, SimulationConnectionManager

__all__ = ["router", "ws_manager", "SimulationConnectionManager"]
