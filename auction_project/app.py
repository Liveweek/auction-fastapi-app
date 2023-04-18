import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import redis
import uvicorn
from database import create_db_and_tables

from routes.auction_api_routes import auction_router
from routes.auth_routes import auth_router
from routes.moderate_routes import moderate_router

from utils.socket_utils import ConnectionManager, redis_conn

app = FastAPI()

manager = ConnectionManager(redis_conn())

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

@app.on_event("startup")
def on_startup():
    asyncio.create_task(manager.consume())
    create_db_and_tables()
    
    
@app.websocket("/ws/{auction_id}")
async def websocket_endpoint(websocket: WebSocket, auction_id: str):
    await manager.connect(websocket, auction_id)
    while True:
        try:
            data = await websocket.receive_json()
        except WebSocketDisconnect:
            manager.disconnect(websocket, auction_id)
        except RuntimeError:
            break


app.include_router(auction_router)
app.include_router(auth_router)
app.include_router(moderate_router)
app.mount("/static", StaticFiles(directory="/app/auction_project/static"), name="static")

def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
