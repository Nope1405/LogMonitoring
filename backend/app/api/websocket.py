"""
WebSocket endpoint for real-time alert streaming.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.websocket_manager import ws_manager

websocket_router = APIRouter()


@websocket_router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for real-time alert notifications.
    The consumer pushes alerts here when anomalies are detected.

    Client usage (JavaScript):
        const ws = new WebSocket('ws://localhost:8000/ws/alerts');
        ws.onmessage = (event) => {
            const alert = JSON.parse(event.data);
            console.log('Alert received:', alert);
        };
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, listen for client messages
            data = await websocket.receive_text()
            # Client can send commands like "ping" or "subscribe"
            if data == "ping":
                await websocket.send_text('{"type": "pong"}')
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
