from celery import Celery
from sqlmodel import Session

import models.db_model as db
from enums import AuctionStatus
from database import engine

worker = Celery('auction_worker', broker='redis://default:redispw@redis_broker:6379')


@worker.task
def open_auction(auction_id: int):
    
    with Session(engine) as session:
        
        auction = session.get(db.Auction, auction_id)
        if auction and auction.lot_status == AuctionStatus.scheduled:
            auction.lot_status = AuctionStatus.auc_open
            
        session.add(auction)
        session.commit()
            
            
            
@worker.task
def close_auction(auction_id: int):
    
    with Session(engine) as session:
        auction = session.get(db.Auction, auction_id)
        
        if auction and auction.lot_status == AuctionStatus.auc_open:
            auction.lot_status = AuctionStatus.auc_closed
            
        session.add(auction)
        session.commit()
        

@worker.task
def print_sus():
    print('suuuuuuuuuuuuuuuuuuuuuuuus')
