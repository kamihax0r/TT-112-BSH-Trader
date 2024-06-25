from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine("sqlite:///cryptodb.db")
Base.metadata.create_all(engine)

def create_session():
    Session = sessionmaker(bind=engine)
    session = Session()    
    return session

def insert_data(session, date, symbol, price):
    new_price = CryptoPrice(symbol=symbol, date=date, close=close, high=high, low=low, open=open)
    session.add(new_price)
    session.commit()
    session.close()

def close_session(session):
    session.close()

class BTCPrice(Base):
    __tablename__ = 'btc_price_data'
    id = Column(Integer, primary_key=True)
    open_time = Column(Integer)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    close_time = Column(Integer)
    quote_asset_volume = Column(Float)
    number_of_trades = Column(Integer)
    taker_buy_base_asset_volume = Column(Float)
    taker_buy_quote_asset_volume = Column(Float)
    ignore = Column(Integer)
    ma200 = Column(Float)
    ma50 = Column(Float)
 
class ETHPrice(Base):
    __tablename__ = 'eth_price_data'
    id = Column(Integer, primary_key=True)
    open_time = Column(Integer)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    close_time = Column(Integer)
    quote_asset_volume = Column(Float)
    number_of_trades = Column(Integer)
    taker_buy_base_asset_volume = Column(Float)
    taker_buy_quote_asset_volume = Column(Float)
    ignore = Column(Integer)
    ma200 = Column(Float)
    ma50 = Column(Float)  
