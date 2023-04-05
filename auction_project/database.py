import datetime
from sqlmodel import SQLModel, Session, create_engine
from auction_project.enums import AuctionStatus



sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
    