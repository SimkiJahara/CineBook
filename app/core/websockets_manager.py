"""
Real-time WebSocket Connection Manager.

This module defines the ConnectionManager class, responsible for handling
active WebSocket connections across different show IDs. It provides methods
for connecting, disconnecting, and broadcasting real-time seat status updates
to all subscribed clients for a specific show.
"""

from typing import Dict, List, Set
from fastapi import WebSocket
import json
from app.schemas.booking import WebSocketSeatUpdate

class ConnectionManager:
    """
    Manages active WebSocket connections grouped by show ID.

    :ivar active_connections: A dictionary storing active WebSocket connections.
        Keys are ``show_id`` (int), and values are dictionaries where keys are
        ``client_id`` (str) and values are the :class:`~fastapi.WebSocket` objects.
    :vartype active_connections: Dict[int, Dict[str, WebSocket]]
    """
    def __init__(self):
        # Dictionary to hold active connections: {show_id: {websocket_client_id: WebSocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}

    async def connect(self, show_id: int, websocket: WebSocket, client_id: str):
        """
        Accepts a WebSocket connection and registers it under the specified show ID and client ID.

        :param show_id: The ID of the show the client is subscribing to.
        :type show_id: int
        :param websocket: The incoming WebSocket connection object.
        :type websocket: fastapi.WebSocket
        :param client_id: A unique identifier for the connecting client.
        :type client_id: str
        """
        await websocket.accept()
        if show_id not in self.active_connections:
            self.active_connections[show_id] = {}
        self.active_connections[show_id][client_id] = websocket

    def disconnect(self, show_id: int, client_id: str):
        """
        Removes a WebSocket connection from the active list.

        If the show ID loses all connections, the show ID key is removed from the
        ``active_connections`` dictionary.

        :param show_id: The ID of the show the client was connected to.
        :type show_id: int
        :param client_id: The unique identifier of the client to disconnect.
        :type client_id: str
        """
        if show_id in self.active_connections and client_id in self.active_connections[show_id]:
            del self.active_connections[show_id][client_id]
            if not self.active_connections[show_id]:
                del self.active_connections[show_id]

    async def broadcast_seat_update(self, show_id: int, seats_data: List[dict]):
        """
        Sends a seat status update to all connected clients for a given show.

        The data is serialized using the Pydantic schema for consistency before
        being sent as a JSON string. Connections that fail to send are automatically
        disconnected.

        :param show_id: The ID of the show to broadcast the update to.
        :type show_id: int
        :param seats_data: A list of dictionaries, each representing a seat's status update.
        :type seats_data: List[dict]
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