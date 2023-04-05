from sqlmodel import SQLModel
from typing import List
from pydantic import BaseModel


import models.base_model as base


class VendorRead(base.VendorBase):
    id: int


class CategoryRead(base.CategoryBase):
    id: int


class CategoryWithAuctionCount(base.CategoryBase):
    id: int
    
    count_of_active_auctions: int | None
    

class UserRead(base.UserBase):
    id: int
    username: str
    email: str


class BetRead(base.BetBase):
    id: int
    bet_user: UserRead | None = None


class AuctionFullRead(base.AuctionBase):
    lot_vendor: VendorRead | None = None
    category: CategoryRead | None = None
    auction_bets: List[BetRead] = []
    
    
class AuctionRead(base.AuctionBase):
    id: int
    
    current_bet: float | None
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
    
class TokenData(BaseModel):
    username: str | None = None
    
    
class AuctionFilter(BaseModel):
    ...
