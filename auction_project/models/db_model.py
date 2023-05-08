from typing import Optional, List
import datetime
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

import models.base_model as base


class Category(base.CategoryBase, table=True):
    """Класс Категории лота аукциона"""
    id:                  Optional[int] = Field(default=None, primary_key=True)
    auctions:            List["Auction"] = Relationship(back_populates = "category")
    


class Auction(base.AuctionBase, table=True):
    """Класс Лота аукциона"""
    id:                 Optional[int] = Field(default=None, primary_key=True)
    
    lot_vendor_id:      Optional[int] = Field(default=None, foreign_key="vendor.id")
    lot_vendor:         Optional["Vendor"] = Relationship(back_populates = "auctions")
    
    category_id:        Optional[int] = Field(default=None, foreign_key="category.id")
    category:           Optional[Category] = Relationship(back_populates = "auctions")
    
    auction_bets:       List["Bet"] = Relationship(back_populates="auction")
    
    user_winner_id:     Optional[int] = Field(default=None, foreign_key='user.id')
    


class Bet(base.BetBase, table=True):
    """Класс Ставки по лоту"""
    
    id:           Optional[int] = Field(default=None, primary_key=True)
    
    auction_id:   Optional[int] = Field(default=None, foreign_key="auction.id") 
    auction:      Optional[Auction] = Relationship(back_populates="auction_bets")
    
    bet_user_id:  Optional[int] = Field(default=None, foreign_key="user.id")
    bet_user:     Optional["User"] = Relationship(back_populates="bets_history")
    
    
class User(base.UserBase, table=True):
    """Класс пользователя платформы аукциона"""
    id:              Optional[int] = Field(default=None, primary_key=True)
    
    hashed_password: str
    vendor_link:     Optional["Vendor"] = Relationship(back_populates="user_link", sa_relationship_kwargs={'uselist': False})
    bets_history:    List[Bet] = Relationship(back_populates="bet_user")
    
    
class Vendor(base.VendorBase, table=True):
    """Класс вендора аукционов"""
    id:                 Optional[int] = Field(default=None, primary_key=True)
    
    auctions:           List[Auction] = Relationship(back_populates="lot_vendor")
    
    user_id:            Optional[int] = Field(default=None, foreign_key="user.id")
    user_link:          Optional[User] = Relationship(back_populates="vendor_link", sa_relationship_kwargs={'uselist': False})
    
    
    

