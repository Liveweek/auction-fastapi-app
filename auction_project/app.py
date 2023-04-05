from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database import create_db_and_tables

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


from routes.auction_api_routes import auction_router
from routes.auth_routes import auth_router

app.include_router(auction_router)
app.include_router(auth_router)


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


def main():
    from models.db_model import Auction, Bet, Vendor, Category, User
    from database import engine
    import datetime
    from sqlmodel import Session
    from enums import AuctionStatus
    create_db_and_tables()
    
    
    # user = User( **{"username": "johndoe",
    #     "email": "johndoe@example.com",
    #     "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    # })
    # with Session(engine) as session:
    #     session.add(user)
    #     # session.add(a)
    #     session.commit()

if __name__ == "__main__":
    main()