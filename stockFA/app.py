from config import logger
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
import yfinance as yf
from tickerlist import ticker_list
from dbconfig import StockPrices, Earnings
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

#Convert Quarter/Year QQYYYY format into timestamp format 
def convertEarningTimestamps(earnings):
    date_strings = []
    for date in earnings['Quarter']:
        year = date[2:]
        quarter = date[:1]
        # Convert the quarter to a month number
        if quarter == "1":
            month = "03"
            days = "31"
        elif quarter == "2":
            month = "06"
            days = "30"
        elif quarter == "3":
            month = "09"
            days = "30"
        elif quarter == "4":
            month = "12"
            days = "31"
        else:
            # Handle any other cases here
            pass
        # Concatenate the month and year to create a date string in the format '%Y-%m-%d %H:%M:%S'
        date_str = year + "-" + month + "-" + days + " 00:00:00"
        # Use the datetime module to convert the date string to a datetime object
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        # Append the datetime object to the list of actual dates
        date_strings.append(date)
        date_strings = list(reversed(date_strings))
    # Take the date strings and turn them into an appropriate index for a dataframe
    date_index = pd.DatetimeIndex(date_strings)
    # Set the index of earnings to the date_index. Because earnings was passed in, it should be modified in place now and ready to go.
    earnings.index = date_index
    return earnings

#Write data to the stock_prices table
def writeStockData(symbol):
    stockPriceData = yf.download(symbol, period='ytd', interval='1d')
    stockPriceData = stockPriceData.reset_index()
    for index, row in stockPriceData.iterrows():
        date = row['Date']
        date = pd.to_datetime(date)
        date = str(date)
        entry = row[['Open', 'High', 'Low', 'Close', 'Volume']]
        #Convert string fields into INTs for the database
        entry = entry.apply(pd.to_numeric)
        stock_price = StockPrices(symbol=t,date=date, open=entry['Open'], high=entry['High'], low=entry['Low'], close=entry['Close'], volume=entry['Volume'])
        session.add(stock_price)
    session.commit()

# Write data to the earnings table
def writeFinancialsData(symbol):
    ticker = yf.Ticker(symbol)
    
    # Get historical earnings data for the specified symbol
    quarterly_income_stmt = ticker.quarterly_income_stmt
    quarterly_earnings = ticker.quarterly_earnings
    quarterly_earnings = quarterly_earnings.reset_index()
    quarterly_cashflow = ticker.quarterly_cashflow
    quarterly_earnings = convertEarningTimestamps(quarterly_earnings)
    
    for date in quarterly_earnings.index:
        #print(quarterly_earnings.loc[date])
        date_string = date.strftime("%Y-%m-%d")
        #Get the index in the dataframe corresponding to which date we're on
        cashflow_data = quarterly_cashflow[date_string]
        income_data = quarterly_income_stmt[date_string]
        #Start putting items into the earnings object so we can write to the database
        #Brad Finn List: Free cash flow - 10 years back, 5 years if they're young, which is very inaccurate
        #              : What % does it grow YOY? That becomes forward growth %. Also look at sector average
        #              : Estimate 10 years of growth at that rate. Multiply the 10th year by a margin 10 is typical, 5 is conservative
        #              : Make up a discount rate (12-15% if the market is 8-10%, so we're looking to kill it)
        #              : Sum it up, get present date value of all future cash flows
        #              : Present Value by Current Shares Outstanding, That should give a rough estimate of stock price
        #              : Use a margin of safety to account for error 30-35% to be conservative, 20% if you think you're a bad ass
        #              : (Maybe look for puts at the safety price if the put delta is about 30)
            
    #session.commit()


if __name__ == '__main__':
    for t in ticker_list:
        #Get the price data in daily candles
        
        #logger.info("Beginning to write stock data to database for stock {}".format(t))
        #Send the stock data to a function to write into the DB
        #writeStockData(t, stockPriceData)
        logger.info("Begginning to write earnings data to the database for stock {}".format(t))
        #Write to the earnings tables to do FA with
        writeFinancialsData(t)
     
      
