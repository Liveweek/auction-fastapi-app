from fastapi import APIRouter, Depends
from sqlmodel import Session

from auction_project.dependencies import get_session
import models.db_model as db


moderate_router = APIRouter(
    prefix="/moderate",
    tags=["moderate"]
)

@moderate_router.get('/init')
def init_data(session: Session = Depends(get_session)):
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
    session.commit()
    
    return {'message': 'Всё готово, ПАГНА!'}