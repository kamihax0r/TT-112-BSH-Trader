'''
This is a function to grab all BTC price data for the last 10 years on a 30m time frame and put it into my database
'''

from config import logger
from flask_sqlalchemy import SQLAlchemy
import datetime 
from datetime import datetime, timedelta
import pandas as pd
from cryptoDBconfig import Base, engine, create_session, ETHPrice, BTCPrice
from binanceAPIconfig import binance

#Database session open so we can write and query the DB
session = create_session()


def get_price_data(pair, days_back):

    # Calculate the start date for the requested data
    start = (datetime.now() - timedelta(days_back)).strftime("%d %b, %Y %I:%M %p")
    end = datetime.now().strftime("%d %b, %Y %I:%M %p")

    # Collect the price data from Binance API
    klines={}
    klines = binance.get_historical_klines(pair, binance.KLINE_INTERVAL_30MINUTE, start, end)

    # Convert the data to a dateframe in pandas
    df = {}
    df =  pd.DataFrame(klines, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])

    print(df.tail(10))
    return df

def writeBTCData(df):
    for index,row in df.iterrows():
        session.add(BTCPrice(open_time=row["Open time"],
                                open=row["Open"],
                                high=row["High"],
                                low=row["Low"],
                                close=row["Close"],
                                volume=row["Volume"],
                                close_time=row["Close time"],
                                quote_asset_volume=row["Quote asset volume"],
                                number_of_trades=row["Number of trades"],
                                taker_buy_base_asset_volume=row["Taker buy base asset volume"],
                                taker_buy_quote_asset_volume=row["Taker buy quote asset volume"],
                                ignore=row["Ignore"]))

    session.commit()
    session.close()


def writeETHData(df):
    for index,row in df.iterrows():
        session.add(ETHPrice(open_time=row["Open time"],
                                open=row["Open"],
                                high=row["High"],
                                low=row["Low"],
                                close=row["Close"],
                                volume=row["Volume"],
                                close_time=row["Close time"],
                                quote_asset_volume=row["Quote asset volume"],
                                number_of_trades=row["Number of trades"],
                                taker_buy_base_asset_volume=row["Taker buy base asset volume"],
                                taker_buy_quote_asset_volume=row["Taker buy quote asset volume"],
                                ignore=row["Ignore"]))

    session.commit()
    session.close()

if __name__ == '__main__':
    # Define the list of crypto currencies you want to get the k-lines for
    symbols = ['BTCUSD', 'ETHUSD']

    # Define the start and end dates for the k-lines
    # Look back x years, this way, if we want days we can just comment out years and use the days variable
    years_lookback = 10
    days = years_lookback * 365 

    #Get the price data
    btcData = get_price_data('BTCUSD', days)
    ethData = get_price_data('ETHUSD', days)
    writeBTCData(btcData)
    writeETHData(ethData)
