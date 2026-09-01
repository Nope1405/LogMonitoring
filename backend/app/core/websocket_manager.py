"""
WebSocket connection manager.
Manages active WebSocket connections and broadcasts alerts in real-time.
"""

import json
from typing import Any

from fastapi import WebSocket


class WebSocketManager:
    """
    Manages WebSocket connections for real-time alert broadcasting.

    Usage:
        manager = WebSocketManager()
        await manager.connect(websocket)
        await manager.broadcast({"type": "alert", "data": {...}})
        manager.disconnect(websocket)
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🔌 WebSocket connected. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"🔌 WebSocket disconnected. Active: {len(self.active_connections)}")

    async def broadcast(self, data: dict[str, Any]):
        """
        Send a message to all connected WebSocket clients.
        Automatically removes dead connections.
        """
        dead_connections = []
        message = json.dumps(data)

        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead_connections.append(connection)

        # Clean up dead connections
        for dead in dead_connections:
            self.disconnect(dead)

    @property
    def connection_count(self) -> int:
        """Number of active WebSocket connections."""
        return len(self.active_connections)


# Singleton instance used across the application
ws_manager = WebSocketManager()
