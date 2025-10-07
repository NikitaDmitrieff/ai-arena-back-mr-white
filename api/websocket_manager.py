"""
WebSocket connection manager for real-time game events.
"""

import json
import logging
from typing import Dict, List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time game updates."""

    def __init__(self):
        # Map game_id -> list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, game_id: str, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection for a game."""
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)
        logger.info(
            f"WebSocket connected for game {game_id}. Total connections: {len(self.active_connections[game_id])}"
        )

    def disconnect(self, game_id: str, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        if game_id in self.active_connections:
            if websocket in self.active_connections[game_id]:
                self.active_connections[game_id].remove(websocket)
                logger.info(
                    f"WebSocket disconnected for game {game_id}. Remaining: {len(self.active_connections[game_id])}"
                )
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]

    async def broadcast_to_game(self, game_id: str, message: dict) -> None:
        """Broadcast a message to all connected clients for a specific game."""
        if game_id not in self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections[game_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(
                    f"Error sending to WebSocket for game {game_id}: {str(e)}"
                )
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(game_id, connection)

    async def send_event(
        self, game_id: str, event_type: str, data: dict
    ) -> None:
        """Send a structured event to all clients watching a game."""
        from datetime import datetime

        message = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast_to_game(game_id, message)


# Global WebSocket manager instance
ws_manager = WebSocketManager()

