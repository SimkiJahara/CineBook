# /core/websockets_manager.py

from typing import Dict, List, Set
from fastapi import WebSocket
import json
from app.schemas.booking import WebSocketSeatUpdate

class ConnectionManager:
    def __init__(self):
        # Dictionary to hold active connections: {show_id: {websocket_client_id: WebSocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}

    async def connect(self, show_id: int, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if show_id not in self.active_connections:
            self.active_connections[show_id] = {}
        self.active_connections[show_id][client_id] = websocket

    def disconnect(self, show_id: int, client_id: str):
        if show_id in self.active_connections and client_id in self.active_connections[show_id]:
            del self.active_connections[show_id][client_id]
            if not self.active_connections[show_id]:
                del self.active_connections[show_id]

    async def broadcast_seat_update(self, show_id: int, seats_data: List[dict]):
        """
        Sends a seat status update to all connected clients for a given show.
        """
        if show_id in self.active_connections:
            # Prepare the data using the Pydantic model for consistency
            payload = json.loads(WebSocketSeatUpdate(
                show_id=show_id, 
                seats=seats_data
            ).json(by_alias=False)) 
            
            json_str = json.dumps(payload, default=str)

            for client_id, connection in list(self.active_connections[show_id].items()):
                try:
                    await connection.send_text(json_str)
                except RuntimeError as e:
                    print(f"Error sending to client {client_id} for show {show_id}: {e}. Disconnecting.")
                    self.disconnect(show_id, client_id)
                except Exception:
                    self.disconnect(show_id, client_id)

manager = ConnectionManager()