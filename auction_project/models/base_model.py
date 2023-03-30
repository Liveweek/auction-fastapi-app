from typing import Optional
from sqlmodel import SQLModel
import datetime


import enums


class AuctionBase(SQLModel):
    lot_name:           str
    lot_description:    str
    lot_photo_path:     Optional[str]
    lot_min_bet:        float
    lot_hot_price:      Optional[float]
    lot_status:         enums.AuctionStatus
    lot_begin_datetime: Optional[datetime.datetime]
    lot_end_datetime:   Optional[datetime.datetime]
    

class CategoryBase(SQLModel):
    name:                str
    description:         str
    category_photo_path: Optional[str]
    

class BetBase(SQLModel):
    bet_datetime: datetime.datetime
    bet_size:     float
    
    
class VendorBase(SQLModel):
    vendor_name:        str
    store_name:         str
    store_phone_number: str
    store_site:         str
    store_address:      Optional[str]
    vendor_photo_path:  Optional[str] 
       

class UserBase(SQLModel):
    email:           str 
    username:        str 
