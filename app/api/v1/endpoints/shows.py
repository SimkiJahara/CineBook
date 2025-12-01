# File: simkijahara/cinebook/CineBook-Nafisa/app/api/v1/endpoints/shows.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from nanoid import generate
from app.core.websockets_manager import manager 
# CORRECT IMPORTS from security.py:
from app.core.security import decode_jwt, InvalidTokenError 
# Import the state constants directly from Starlette to fix the previous AttributeError
from starlette.websockets import WebSocketState 

router = APIRouter(
    prefix="/shows",
    tags=["Shows"],
)
# ... (read_show endpoint)

@router.websocket("/ws/{show_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    show_id: int,
    token: str = Query(None), # Added for authentication
    client_id: str = Query(generate(), alias="clientId"), 
):
    
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication token missing.")
        return

    try:
        # AUTHENTICATION STEP:
        payload = decode_jwt(token) # Uses the function defined in security.py
        user_id = payload.get("user_id") 

        if not user_id:
             await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token payload: User ID missing.")
             return

        await websocket.accept()
        manager.connect(show_id, websocket, client_id)
        
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(show_id, client_id)
    except InvalidTokenError:
        # Handles expired or invalid JWT (raised by decode_jwt)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired authentication token.")
    except Exception as e:
        # Handles other potential errors (like connection failure)
        print(f"WebSocket Internal Error for show {show_id}, client {client_id}: {e}")
        
        if websocket.client_state == WebSocketState.CONNECTED:
            manager.disconnect(show_id, client_id)
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Internal processing failed.")