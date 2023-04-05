import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, or_
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
    results = session.exec(statement)
    
    return results.all()
    
    
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
        category_with_count_of_auctions.count_of_active_auctions = len(filter(lambda elem: elem.lot_status in (AuctionStatus.auc_open, AuctionStatus.scheduled), category.auctions))
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
    result = session.exec(statement)
    return result.all()



@auction_router.get('/auctions/vendor/{vendor_id}')
def get_auctions_by_vendor():
    ...



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
        return JSONResponse(404, context={"message": "Аукцион не найден"})
    
    
    bet = db.Bet(
        bet_datetime=datetime.datetime.now(),
        bet_size=bet_size,
        auction=auction,
        bet_user=current_user
    )
    
    session.add(bet)
    session.commit()
    
    return bet
    