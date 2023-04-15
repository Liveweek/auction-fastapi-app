from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from database import create_db_and_tables

from routes.auction_api_routes import auction_router
from routes.auth_routes import auth_router
from routes.moderate_routes import moderate_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(auction_router)
app.include_router(auth_router)
app.include_router(moderate_router)
app.mount("/static", StaticFiles(directory="/app/auction_project/static"), name="static")

def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
