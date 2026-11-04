"""Unit tests for RoboTrace 3D simulation WebSocket endpoint."""

import json
import pytest
from starlette.testclient import TestClient

from backend.main import app


class TestSimulationWebSocket:
    """Verify live telemetry WebSocket streaming."""

    def test_websocket_ping_pong_and_subscribe(self):
        client = TestClient(app)
        with client.websocket_connect("/ws/simulation") as websocket:
            # 1. Test PING
            websocket.send_text(json.dumps({"type": "PING"}))
            response_text = websocket.receive_text()
            data = json.loads(response_text)
            assert data["type"] == "PONG"
            assert "timestamp" in data

            # 2. Test SUBSCRIBE
            websocket.send_text(json.dumps({
                "type": "SUBSCRIBE",
                "data": {"mission_id": 2},
            }))
            sub_text = websocket.receive_text()
            sub_data = json.loads(sub_text)
            assert sub_data["type"] == "SUBSCRIBED"
            assert sub_data["data"]["mission_id"] == 2

    def test_websocket_broadcast_distribution(self):
        from backend.api.websocket import ws_manager
        client = TestClient(app)

        with client.websocket_connect("/ws/simulation") as ws1:
            with client.websocket_connect("/ws/simulation") as ws2:
                assert len(ws_manager.active_connections) == 2

                # Manually broadcast message
                import asyncio
                test_event = {
                    "type": "simulation_event",
                    "timestamp": "2026-11-04T05:00:00Z",
                    "data": {"event": "TEST_BROADCAST"},
                }
                asyncio.run(ws_manager.broadcast_message(test_event))

                # Both clients receive the message
                msg1 = json.loads(ws1.receive_text())
                msg2 = json.loads(ws2.receive_text())
                assert msg1["type"] == "simulation_event"
                assert msg2["type"] == "simulation_event"
                assert msg1["data"]["event"] == "TEST_BROADCAST"

            # Once ws2 context manager exits, it is disconnected
            assert len(ws_manager.active_connections) <= 1
