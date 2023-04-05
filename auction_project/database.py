import datetime
from sqlmodel import SQLModel, Session, create_engine
from auction_project.enums import AuctionStatus



sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.clear()
    SQLModel.metadata.create_all(engine)
    
    from auction_project.models.db_model import Auction, Bet, Category, Vendor
    c = Category(
        name="Шляпы",
        description="Они всем как раз",
        category_photo_path="/categories/ssss"
    )
    v = Vendor(
        vendor_name="Алладин ебучий",
        store_name="Магазин у Али Бабы",
        store_phone_number="22-22-888",
        store_site=r"http://www.google.com",
        vendor_photo_path="/vendor/123123"
    )
    a = Auction(
        lot_name="Шляпа султана",
        lot_description="Ебаная шляпа султана",
        lot_min_bet=11.5,
        lot_status=AuctionStatus.auc_open,
        category=c,
        lot_vendor=v
    )
    b1 = Bet(
        bet_datetime=datetime.datetime.now(),
        bet_size=100.
    )
    b2 = Bet(
        bet_datetime=datetime.datetime.now(),
        bet_size=200.
    )
    a.auction_bets.extend([b1, b2])
    
    with Session(engine) as session:
        session.add(a)
        session.commit()
    
    