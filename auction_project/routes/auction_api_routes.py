import datetime
from typing import Annotated, List
import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, or_, and_
import sqlalchemy


import models.db_model as db
import models.api_model as api
from utils.auth_utils import get_current_user


from dependencies import get_session
from enums import AuctionStatus



auction_router = APIRouter(
    prefix="/api_v1",
    tags=["auction"]
)


@auction_router.get('/me', response_model=api.UserRead)
def get_me(user: db.User = Depends(get_current_user)):
    return user



@auction_router.get('/auctions/', response_model=List[api.AuctionRead])
def get_auctions(
        *,
        limit: int = 10,
        offset: int = 0,
        session: Session = Depends(get_session)
    ):
    statement = select(db.Auction).offset(offset).limit(limit)
    results = session.exec(statement).all()
    
    def get_current_bet(auction):
        auction_with_last_bet = api.AuctionRead(**auction.dict())
        auction_with_last_bet.current_bet = auction.auction_bets[-1].bet_size
        return auction_with_last_bet
    
    return list(map(get_current_bet, results))
        
    
    
@auction_router.get('/auctions/status/{status_code}', response_model=List[api.AuctionRead])
def get_auctions_by_status(
        *,
        status_code: AuctionStatus = AuctionStatus.auc_open,
        limit: int = 10,
        offset: int = 0,
        session: Session = Depends(get_session)
    ):
    
    statement = (select(db.Auction)
                    .where(db.Auction.lot_status == status_code)
                    .offset(offset)
                    .limit(limit))
    results = session.exec(statement).all()
    
    def get_current_bet(auction):
        auction_with_last_bet = api.AuctionRead(**auction.dict())
        auction_with_last_bet.current_bet = auction.auction_bets[-1].bet_size
        return auction_with_last_bet
    
    return list(map(get_current_bet, results))
    
    
@auction_router.get('/auctions/category', response_model=List[api.CategoryWithAuctionCount])
def get_category_list(
        *,
        offset: int = 0,
        limit: int = 5,
        session: Session = Depends(get_session)
    ):
    statement = (select(db.Category)
                    .offset(offset)
                    .limit(limit))
    
    result = session.exec(statement)
    
    def add_cnt_of_auctions(category):
        category_with_count_of_auctions = api.CategoryWithAuctionCount(**category.dict())
        category_with_count_of_auctions.count_of_active_auctions = len(list(filter(lambda elem: elem.lot_status in (AuctionStatus.auc_open, AuctionStatus.scheduled), category.auctions)))
        return category_with_count_of_auctions
    
    result = list(map(add_cnt_of_auctions, result))
    
    return result

    
@auction_router.get('/auctions/category/{category_id}', response_model=List[api.AuctionRead])
def get_auctions_by_category(
        *,
        category_id: int,
        session: Session = Depends(get_session)
    ):
    statement = (select(db.Auction)
                    .where(db.Auction.category_id == category_id)
                    .where(or_(db.Auction.lot_status == AuctionStatus.auc_open, 
                               db.Auction.lot_status == AuctionStatus.scheduled)))
    
    results = session.exec(statement).all()
    
    def get_current_bet(auction):
        auction_with_last_bet = api.AuctionRead(**auction.dict())
        auction_with_last_bet.current_bet = auction.auction_bets[-1].bet_size
        return auction_with_last_bet
    
    return list(map(get_current_bet, results))



@auction_router.get('/auctions/vendor/{vendor_id}', response_model=List[api.AuctionRead])
def get_auctions_by_vendor(
    *,
    vendor_id: int,
    session: Session = Depends(get_session)
    ):
    
    statement = select(db.Auction). \
                    where(db.Auction.lot_vendor_id == vendor_id). \
                    where(or_(db.Auction.lot_status == AuctionStatus.auc_open,
                              db.Auction.lot_status == AuctionStatus.scheduled)). \
                    order_by(db.Auction.lot_begin_datetime)
                    
    results = session.exec(statement)
    
    def get_current_bet(auction):
        auction_with_last_bet = api.AuctionRead(**auction.dict())
        auction_with_last_bet.current_bet = auction.auction_bets[-1].bet_size
        return auction_with_last_bet
    
    return list(map(get_current_bet, results))



@auction_router.get('/auction/{auction_id}', response_model=api.AuctionFullRead)
def get_auction_by_id(
        *,
        auction_id: int,
        session: Session = Depends(get_session)
    ):
    statement = (select(db.Auction).where(db.Auction.id == auction_id))
    try:
        result = session.exec(statement).one()
    except sqlalchemy.exc.NoResultFound:
        return JSONResponse(status_code=404, content={"message": "Аукцион не найден"})
    else:
        return result
    
    
@auction_router.post('/auction', response_model=api.AuctionFullRead)
def create_auction(
    *,
    auction: api.AuctionCreate,
    session: Session = Depends(get_session),
    current_user: db.User = Depends(get_current_user)
    ):
    
    if not current_user.vendor_link:
        return JSONResponse(402, context={"message": "У пользователя нет привязки к Вендору"})
    
    #TODO: добавить реализацию создания объекта аукциона
    # + добавить модель для ввода (проприсать необходимые атрибуты)
    auction = db.Auction()
    
    session.add(auction)
    session.commit()
    
    session.refresh(auction)
    
    return auction
    
    
    
@auction_router.delete('/auction/{auction_id}', response_model=api.AuctionRead)
def delete_auction(
    *,
    auction_id: int,
    session: Session = Depends(get_session)
    ):
    deleted_auction = session.get(db.Auction, auction_id)
    if not deleted_auction:
        return JSONResponse(status_code=404, content={"message": "Аукцион не найден"})
    
    session.delete(deleted_auction)
    session.commit()
    return deleted_auction
    


@auction_router.post('/auction/{auction_id}/bet', response_model=api.BetRead)
def make_bet(
    *,
    auction_id: int,
    bet_size: float,
    current_user: db.User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    auction = session.get(db.Auction, auction_id)
    
    if not auction:
        return JSONResponse(status_code=404, content={"message": "Аукцион не найден"})
    
    if auction.lot_status == AuctionStatus.auc_closed:
        return JSONResponse(status_code=402, content={"message": "Аукцион уже закрыт"})
                                          

    bet = db.Bet(
        bet_datetime=datetime.datetime.now(),
        bet_size=bet_size,
        auction=auction,
        bet_user=current_user
    )
    
    session.add(bet)
    session.commit()
    
    return bet


@auction_router.post('/auction/{auction_id}/buy_now', response_model=api.AuctionRead)
def buy_auction_now(
    *,
    auction_id: int,
    current_user: db.User = Depends(get_current_user),
    session: Session = Depends(get_session)
    ):
    
    auction = session.get(db.Auction, auction_id)
    
    if not auction:
        return JSONResponse(status_code=404, content={"message": "Аукцион не найден"})
    
    if auction.lot_status == AuctionStatus.auc_closed:
        return JSONResponse(status_code=402, content={"message": "Аукцион уже закрыт"})
    
    if not auction.lot_hot_price:
        return JSONResponse(status_code=402, content={"message": "Аукцион нельзя выкупить"})
    
    auction.user_winner_id = current_user.id
    auction.lot_status = AuctionStatus.auc_closed
    auction.lot_end_datetime = datetime.datetime.now()
    
    bet = db.Bet(
        bet_datetime=datetime.datetime.now(),
        bet_size=auction.lot_hot_price,
        auction=auction,
        bet_user=current_user
    )
    
    session.add(bet)
    session.commit()
    
    # refresh auction object
    session.refresh(auction) #TODO: надо проверить, как это работает
    
    def get_current_bet(auction):
        auction_with_last_bet = api.AuctionRead(**auction.dict())
        auction_with_last_bet.current_bet = auction.auction_bets[-1].bet_size
        return auction_with_last_bet
    
    return get_current_bet(auction)
    

@auction_router.get("/vendors", response_model=List[api.VendorShortRead])
def get_vendors(
    *,
    offset: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session)
    ):
    
    statement = select(db.Vendor). \
                    offset(offset). \
                    limit(limit)
                    
    return session.exec(statement).all()



@auction_router.get("/vendor/{vendor_id}", response_model=api.VendorRead)
def get_vendor_by_id(
    *,
    vendor_id: int,
    session: Session = Depends(get_session)
    ):
    
    vendor = session.get(db.Vendor, vendor_id)
    
    if not vendor:
        return JSONResponse(status_code=404, content={"message": "Вендор не найден"})
    
    return vendor


@auction_router.post("/vendor", response_model=api.VendorRead)
def create_vendor(
    *,
    vendor_name:        Annotated[str, Form()],
    store_name:         Annotated[str, Form()],
    store_phone_number: Annotated[str, Form()],
    store_site:         Annotated[str, Form()],
    store_address:      Annotated[str, Form()],
    vendor_photo:       UploadFile = File(),
    current_user: db.User = Depends(get_current_user),
    session: Session = Depends(get_session),
    ):
    
    if current_user.vendor_link:
        return JSONResponse(status_code=401, content={"message": "У данного пользователя уже есть вендор"})
    
    file_type = vendor_photo.filename.split('.')[-1]
    data = vendor_photo.file.read()
    
    vendor = db.Vendor(
        vendor_name        = vendor_name,
        store_name         = store_name,
        store_phone_number = store_phone_number,
        store_site         = store_site,
        store_address      = store_address,
        user_link          = current_user
    )
    
    vendor.vendor_photo_path = rf'/vendor/{uuid.uuid4().__str__()}.{file_type}'

    with open('/app/auction_project/static' + vendor.vendor_photo_path, 'wb') as buffer:
        buffer.write(data)
        
    session.add(vendor)
    session.commit()
    
    session.refresh(vendor)
    
    return vendor
    