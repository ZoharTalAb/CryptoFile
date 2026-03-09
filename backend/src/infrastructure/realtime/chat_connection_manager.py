from collections import defaultdict
from typing import DefaultDict, List

from fastapi import WebSocket


class ChatConnectionManager:
    def __init__(self):
        self._connections: DefaultDict[int, List[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self._connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id not in self._connections:
            return

        if websocket in self._connections[user_id]:
            self._connections[user_id].remove(websocket)

        if not self._connections[user_id]:
            del self._connections[user_id]

    async def send_to_user(self, user_id: int, event: dict):
        dead_connections: List[WebSocket] = []

        for websocket in self._connections.get(user_id, []):
            try:
                await websocket.send_json(event)
            except Exception:
                dead_connections.append(websocket)

        for websocket in dead_connections:
            self.disconnect(user_id, websocket)

    async def broadcast_to_users(self, user_ids: list[int], event: dict):
        for user_id in user_ids:
            await self.send_to_user(user_id, event)

    def is_connected(self, user_id: int) -> bool:
        return user_id in self._connections and len(self._connections[user_id]) > 0


chat_connection_manager = ChatConnectionManager()
