import datetime
from fastapi import APIRouter, Depends
from sqlmodel import Session, delete

from dependencies import get_session
from enums import AuctionStatus
import models.db_model as db


moderate_router = APIRouter(
    prefix="/moderate",
    tags=["moderate"]
)

@moderate_router.get('/init')
def init_data(session: Session = Depends(get_session)):
    
    session.exec(delete(db.Bet))
    session.exec(delete(db.Auction))
    session.exec(delete(db.Vendor))
    session.exec(delete(db.Category))
    session.exec(delete(db.User))
    
    session.commit()
    
    
    c = db.Category(
        name="Шляпы",
        description="Они всем как раз",
        category_photo_path="/categories/ssss"
    )
    v = db.Vendor(
        vendor_name="Алладин ебучий",
        store_name="Магазин у Али Бабы",
        store_phone_number="22-22-888",
        store_site=r"http://www.google.com",
        vendor_photo_path="/vendor/123123"
    )
    a = db.Auction(
        lot_name="Шляпа султана",
        lot_description="Ебаная шляпа султана",
        lot_min_bet=11.5,
        lot_hot_price=2000,
        lot_status=AuctionStatus.auc_open,
        category=c,
        lot_vendor=v
    )
    b1 = db.Bet(
        bet_datetime=datetime.datetime.now(),
        bet_size=100.
    )
    b2 = db.Bet(
        bet_datetime=datetime.datetime.now(),
        bet_size=200.
    )
    a.auction_bets.extend([b1, b2])
    
    session.add(a)
    
    user = db.User( **{"username": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    })
    session.add(user)
    session.commit()
    return {'message': 'Всё готово, ПАГНА!'}