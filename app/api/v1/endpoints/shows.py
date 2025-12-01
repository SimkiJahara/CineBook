"""
Show and Real-time Seat Status Endpoints.

This module defines the API routes related to show information and provides
a WebSocket endpoint for clients to receive real-time updates on seat availability
and reservation status for a specific show.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from nanoid import generate # You may need to install nanoid (pip install nanoid)
from app.core.websockets_manager import manager # Import the global manager

router = APIRouter(
    prefix="/shows",
    tags=["Shows"],
)

# Placeholder for an example HTTP endpoint (e.g., getting show details)
@router.get("/{show_id}", summary="Get detailed information for a show")
def read_show(show_id: int):
    """
    Retrieves basic show and screen layout information.

    This is a standard HTTP GET request used to fetch static or initial
    information about a show before a user connects to the real-time feed.

    :param show_id: The unique integer ID of the show.
    :type show_id: int
    :return: A dictionary containing show details and layout information.
    :rtype: dict
    """
    return {"show_id": show_id, "status": "Available", "layout": "A1, A2, B1, B2..."}


# WebSocket Endpoint for Real-time Seat Updates
@router.websocket("/ws/{show_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    show_id: int,
    # Use nanoid to generate a unique ID for the client connection
    client_id: str = Query(generate(), alias="clientId"), 
):
    """
    Handles WebSocket connections for real-time seat status updates.

    Clients connect to this endpoint to subscribe to live updates for a specific
    show. The server pushes messages when a seat is reserved, confirmed, or
    released.

    .. code-block:: none

        Connect URL: ws://<server_url>/api/v1/shows/ws/{show_id}?clientId=<unique_id>

    :param websocket: The WebSocket object representing the client connection.
    :type websocket: fastapi.WebSocket
    :param show_id: The ID of the show the client wants to monitor.
    :type show_id: int
    :param client_id: A unique identifier for the client connection (auto-generated if not provided).
    :type client_id: str
    :raises WebSocketDisconnect: If the client closes the connection.
    """
    
    try:
        # Connect the client and accept the connection
        await manager.connect(show_id, websocket, client_id)
        
        # Keep the connection open - server will push data when seat status changes
        while True:
            # We must await something to keep the connection open, even if we don't expect messages.
            # Client could send a ping or close message.
            await websocket.receive_text()

    except WebSocketDisconnect:
        # Client disconnected
        manager.disconnect(show_id, client_id)
    except Exception as e:
        print(f"WebSocket Error for show {show_id}, client {client_id}: {e}")
        manager.disconnect(show_id, client_id)