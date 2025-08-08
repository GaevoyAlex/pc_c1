from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

from app.services.market.websocket_manager import manager

router = APIRouter()

@router.websocket("/ws/{token_id}")
async def websocket_endpoint(websocket: WebSocket, token_id: str):
    await manager.connect(websocket, token_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong", "timestamp": message.get("timestamp")}), 
                    websocket
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[ERROR][WebSocket] - Connection error: {e}")
        manager.disconnect(websocket)