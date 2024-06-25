import yfinance as yf
from config import logger
import json
from sqlalchemy.orm import scoped_session
from config import db_session

def get_earnings(stock_symbol:str):
    stock = yf.Ticker(stock_symbol)
    earnings = stock.earnings.tail(4)
    quarterlyEarnings = stock.quarterly_earnings.tail(4)
    logger.info("Earnings for {}: {}".format(stock_symbol, json.dumps(earnings.to_dict(), indent=4)))
    logger.info("Quarterly Earnings look like this {}:{}".format(stock_symbol,json.dumps(quarterlyEarnings.to_dict(), indent=4)))
    return earnings

def get_all_earnings(stock_symbols):
    for symbol in stock_symbols:
        # Get the historical price data for the last 10 years
        stock_prices = yf.download(symbol, start='2010-01-01')
        # Get the historical earnings data for the last 10 years
        stock_earnings = yf.download(symbol, start='2010-01-01', actions=True)
        
        # Write the price data to the SQLite database
        stock_prices.to_sql('stock_prices', engine, if_exists='append')
        # Write the earnings data to the SQLite database
        stock_earnings.to_sql('stock_earnings', engine, if_exists='append')
