import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, File, UploadFile, Form
from fastapi.responses import JSONResponse
from sqlmodel import Session, delete
import uuid


from dependencies import get_session
from enums import AuctionStatus
import models.db_model as db
import models.api_model as api 
import models.base_model as base


import auction_worker


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


@moderate_router.post('/category', response_model=api.CategoryRead)
def create_category(
        name: Annotated[str, Form()],
        description: Annotated[str, Form()],
        category_file: UploadFile = File(), 
        session: Session = Depends(get_session)
    ):
    
    file_type = category_file.filename.split('.')[-1]
    data = category_file.file.read()
    
    category = db.Category(name=name, description=description)
    category.category_photo_path = rf'/categories/{uuid.uuid4().__str__()}.{file_type}'
    
    with open('/app/auction_project/static' + category.category_photo_path, 'wb') as buffer:
        buffer.write(data)
        
    session.add(category)
    session.commit()
    return category


@moderate_router.post('/auction/{auction_id}/accept', response_model=base.AuctionBase)
def accept_auction(
        *,
        auction_id: int,
        session: Session = Depends(get_session)
    ):
    
    auction = session.get(db.Auction, auction_id)
    
    
    if not auction:
        return JSONResponse(status_code=404, content={"message": "Аукцион не найден"})
    
    auction.lot_status = AuctionStatus.scheduled        
    
    auction_worker.open_auction.apply_async(
        eta=datetime.datetime.now() + datetime.timedelta(seconds=15),
        args=(auction.id,)
    )
    
    
    session.add(auction)
    session.commit()
    
    return auction
    
    
    
@moderate_router.post('/auction/{auction_id}/decline')
def decline_auction(
     *,
        auction_id: int,
        session: Session = Depends(get_session)
    ):
    
    auction = session.get(db.Auction, auction_id)
    
    
    if not auction:
        return JSONResponse(status_code=404, content={"message": "Аукцион не найден"})
    
    auction.lot_status = AuctionStatus.auc_closed        
    
    session.add(auction)
    session.commit()
    
    return auction


@moderate_router.get('/test')
def run_celery():
    auction_worker.print_sus.apply_async(eta=datetime.datetime.now() + datetime.timedelta(seconds=15))
    
    return {"message": "SUUUUUUUUUUUUUUUS"}
    
    