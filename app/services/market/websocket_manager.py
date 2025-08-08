import asyncio
import json
from typing import Dict, Set, List
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import time

from .coingecko_service import coingecko_service

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.connection_tokens: Dict[WebSocket, str] = {}
        self.update_tasks: Dict[str, asyncio.Task] = {}
        
    async def connect(self, websocket: WebSocket, token_id: str):
        await websocket.accept()
        
        if token_id not in self.active_connections:
            self.active_connections[token_id] = set()
        
        self.active_connections[token_id].add(websocket)
        self.connection_tokens[websocket] = token_id
        
        if token_id not in self.update_tasks:
            self.update_tasks[token_id] = asyncio.create_task(
                self._price_update_loop(token_id)
            )
        
        print(f"[INFO][WebSocket] - New connection for {token_id}, total: {len(self.active_connections[token_id])}")
    
    def disconnect(self, websocket: WebSocket):
        token_id = self.connection_tokens.get(websocket)
        if token_id and token_id in self.active_connections:
            self.active_connections[token_id].discard(websocket)
            
            if not self.active_connections[token_id]:
                del self.active_connections[token_id]
                if token_id in self.update_tasks:
                    self.update_tasks[token_id].cancel()
                    del self.update_tasks[token_id]
                print(f"[INFO][WebSocket] - No more connections for {token_id}, stopped updates")
        
        if websocket in self.connection_tokens:
            del self.connection_tokens[websocket]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"[ERROR][WebSocket] - Failed to send message: {e}")
    
    async def broadcast_to_token(self, token_id: str, message: str):
        if token_id not in self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections[token_id].copy():
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"[ERROR][WebSocket] - Connection failed, removing: {e}")
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)
    
    async def _price_update_loop(self, token_id: str):
        while token_id in self.active_connections and self.active_connections[token_id]:
            try:
                price_data = await coingecko_service.get_token_current_price(token_id)
                
                if price_data:
                    message = {
                        "type": "price_update",
                        "data": price_data
                    }
                    await self.broadcast_to_token(token_id, json.dumps(message))
                
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                print(f"[INFO][WebSocket] - Price update loop cancelled for {token_id}")
                break
            except Exception as e:
                print(f"[ERROR][WebSocket] - Error in price update loop for {token_id}: {e}")
                await asyncio.sleep(60)

manager = ConnectionManager()