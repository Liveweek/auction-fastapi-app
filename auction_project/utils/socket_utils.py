import asyncio
from collections import defaultdict
import json

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self, redis_connection):
        self.redis_connection = redis_connection
        self.active_connections = defaultdict(list)


    async def connect(self, websocket: WebSocket, auction_id: int):
        await websocket.accept()
        self.active_connections[auction_id].append(websocket)


    def disconnect(self, websocket: WebSocket, auction_id: int):
        self.active_connections[auction_id].remove(websocket)


    async def broadcast(self, message: dict, auction_id: int):
        for connection in self.active_connections[auction_id]:
            try:
                await connection.send_json(message)
                print(f"sent {message}")
            except Exception as e:
                pass

    async def consume(self):
        print("started to consume")
        sub = self.redis_connection.pubsub()
        sub.subscribe('channel')
        while True:
            await asyncio.sleep(0.01)
            message = sub.get_message(ignore_subscribe_messages=True)
            if message is not None and isinstance(message, dict):
                
                # ЧТО ЗА СООБЩЕНИЕ БУДЕТ ????
                msg = json.loads(message.get('data'))
                await self.broadcast(msg['message'], msg['auction_id'])
