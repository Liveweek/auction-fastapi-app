from fastapi import FastAPI
import uvicorn
from database import create_db_and_tables

from routes.auction_api_routes import auction_router
from routes.auth_routes import auth_router

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(auction_router)
app.include_router(auth_router)


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)


def main():
    from models.db_model import Auction, Bet, Vendor, Category, User
    from database import engine
    import datetime
    from sqlmodel import Session
    from enums import AuctionStatus
    create_db_and_tables()
    # c = Category(
    #     name="Шляпы",
    #     description="Они всем как раз",
    #     category_photo_path="/categories/ssss"
    # )
    # v = Vendor(
    #     vendor_name="Алладин ебучий",
    #     store_name="Магазин у Али Бабы",
    #     store_phone_number="22-22-888",
    #     store_site=r"http://www.google.com",
    #     vendor_photo_path="/vendor/123123"
    # )
    # a = Auction(
    #     lot_name="Шляпа султана",
    #     lot_description="Ебаная шляпа султана",
    #     lot_min_bet=11.5,
    #     lot_status=AuctionStatus.auc_open,
    #     category=c,
    #     lot_vendor=v
    # )
    # b1 = Bet(
    #     bet_datetime=datetime.datetime.now(),
    #     bet_size=100.
    # )
    # b2 = Bet(
    #     bet_datetime=datetime.datetime.now(),
    #     bet_size=200.
    # )
    # a.auction_bets.extend([b1, b2])
    
    user = User( **{"username": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    })
    with Session(engine) as session:
        session.add(user)
        # session.add(a)
        session.commit()

if __name__ == "__main__":
    main()