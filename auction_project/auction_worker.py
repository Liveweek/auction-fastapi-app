import datetime
import json
from celery import Celery
import redis
from sqlmodel import Session

import models.db_model as db
from enums import AuctionStatus
from database import engine

from utils.socket_utils import redis_conn


worker = Celery('auction_worker', broker='redis://default:redispw@redis-broker:6379')


@worker.task
def open_auction(auction_id: int):
    
    with Session(engine) as session:
        
        auction = session.get(db.Auction, auction_id)
        if auction and auction.lot_status == AuctionStatus.scheduled:
            auction.lot_status = AuctionStatus.auc_open
            
        session.add(auction)
        session.commit()
            
        rds = redis.StrictRedis('redis-socket')
        rds.publish(
            'channel',
            json.dumps({
                "auction_id": str(auction_id),
                "data" : {
                    "event_type": "open",
                    "datetime": datetime.datetime.now().strftime('%Y-%m-%dT%H:%m:%S.%f')
                }
            })
        )
            
            
@worker.task
def close_auction(auction_id: int):
    
    with Session(engine) as session:
        auction = session.get(db.Auction, auction_id)
        
        if auction and auction.lot_status == AuctionStatus.auc_open:
            auction.lot_status = AuctionStatus.auc_closed
            
        session.add(auction)
        session.commit()
        
        rds = redis.StrictRedis('redis-socket')
        rds.publish(
            'channel',
            json.dumps({
                "auction_id": str(auction_id),
                "data" : {
                    "event_type": "close",
                    "datetime": datetime.datetime.now().strftime('%Y-%m-%dT%H:%m:%S.%f')
                }
            })
        )
        

@worker.task
def print_sus():
    print('suuuuuuuuuuuuuuuuuuuuuuuus')
