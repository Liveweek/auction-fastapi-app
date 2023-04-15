import asyncio
from collections import defaultdict
from functools import lru_cache
import json

from fastapi import WebSocket
import redis


@lru_cache(maxsize=1)
def redis_conn():
    return redis.StrictRedis('redis-socket')


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
                msg = json.loads(message.get('data'))
                await self.broadcast(msg['data'], msg['auction_id'])
