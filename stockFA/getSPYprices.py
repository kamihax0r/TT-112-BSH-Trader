'''
This is a function to grab all SPY price data for the last 10 years on a daily time frame and put it into my database
'''

from config import logger
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
import yfinance as yf
from dbconfig import SPYPrices
from datetime import datetime
import pandas as pd

# Connect to the database
engine = create_engine('sqlite:///stockdb.db')
Base = declarative_base()

# Create the tables
Base.metadata.create_all(bind=engine)

# Create a session to add data to the database
Session = sessionmaker(bind=engine)
session = Session()

#initialize ticker
ticker_list = []

#Write data to the stock_prices table
def writeStockData(symbol):
    stockPriceData = yf.download(symbol, period='10y', interval='1d')
    stockPriceData = stockPriceData.reset_index()
    for index, row in stockPriceData.iterrows():
        date = row['Date']
        date = pd.to_datetime(date)
        date = str(date)
        entry = row[['Open', 'High', 'Low', 'Close', 'Volume']]
        #Convert string fields into INTs for the database
        entry = entry.apply(pd.to_numeric)
        stock_price = SPYPrices(symbol=t,date=date, open=entry['Open'], high=entry['High'], low=entry['Low'], close=entry['Close'], volume=entry['Volume'])
        session.add(stock_price)
    session.commit()


if __name__ == '__main__':
    ticker_list = ['SPY']
    for t in ticker_list:
        logger.info("Beginning to write stock data to database for stock {}".format(t))
        #Send the stock data to a function to write into the DB
        writeStockData(t)
        
