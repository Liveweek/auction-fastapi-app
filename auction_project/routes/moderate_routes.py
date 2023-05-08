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
from utils.auth_utils import get_password_hash


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
    
    v = db.Vendor(
        vendor_name="Али Баба",
        store_name="Магазин у Али Бабы",
        store_phone_number="22-22-888",
        store_site=r"http://www.google.com"
    )
    
    vendor_user = db.User(
        username="vendor",
        email="vendor_user@mail.ru",
        hashed_password=get_password_hash("vendor"),
        vendor_link=v
    )
    
    user1 = db.User(
        username="sss",
        email="sss@sss.com",
        hashed_password=get_password_hash("sss")
    )    
    
    user2 = db.User(
        username="ddd",
        email="ddd@ddd.com",
        hashed_password=get_password_hash("ddd")
    )
    
    session.add(vendor_user)
    session.add(user1)
    session.add(user2)
    session.commit()
    return {'message': 'Тестовые данные успешно инициализированы!'}


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
        eta=auction.lot_begin_datetime - datetime.timedelta(hours=3),
        kwargs={"auction_id": auction.id}
    )
    
    auction_worker.close_auction.apply_async(
        eta=auction.lot_end_datetime - datetime.timedelta(hours=3),
        kwargs={"auction_id": auction.id}
    )
    
    session.add(auction)
    session.commit()
    
    return auction
    
    
    
@moderate_router.post('/auction/{auction_id}/decline', response_model=base.AuctionBase)
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