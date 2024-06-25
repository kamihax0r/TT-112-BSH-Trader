from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Define the stock_prices and earnings tables
class StockPrices(Base):
    __tablename__ = 'stock_prices'
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    date = Column(Integer)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)

class Earnings(Base):
    __tablename__ = 'earnings'
    id = Column(Integer, primary_key=True)
    date = Column(Integer)
    earnings = Column(Float)

class SPYPrices(Base):
    __tablename__ = 'spy_prices'
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    date = Column(Integer)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
