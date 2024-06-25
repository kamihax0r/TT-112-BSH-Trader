'''
This is a function to read the 50 and 200 MA on the 30-min BTC chart
Long conditions: 50 MA crosses from below 200MA to above it
Short conditions: 50 MA crosses from above to below 200MA
Stop: <need to figure this ou>
'''

from config import logger
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from cryptoDBconfig import Base, engine, create_session, ETHPrice, BTCPrice
from binanceAPIconfig import binance
from datetime import datetime, timedelta
import statistics

#Database session open so we can write and query the DB
session = create_session()

def determine_crossover(row):
    if row.ma50 > row.ma200:
        return "Bullish"
    elif row.ma50 < row.ma200:
        return "Bearish"
    else:
        return None

#The regular KC function, probably best for use with small sample until the bigger set can be trained
#Assume we don't know the win/loss because I'm moving to percentage win/loss and don't have the data yet
def kelly_criterion(win_prob):
    lose_prob = 1 - win_prob
    odds = win_prob/lose_prob
    bet_size = win_prob - (1 - win_prob) / (odds + 1)
    return bet_size


def buy(betSize, bankroll, invested, buyPrice, basis, currentEthStack):
    #Just to make sure we still have money to spend
    if bankroll > 10000:
        bankroll -= betSize #Take out 10k
        ethAmt = betSize / buyPrice #Figure out how much ETH that buys
        #Set your basis
        if currentEthStack > 0:
            basis = ((currentEthStack*basis) + (ethAmt*buyPrice))/ (ethAmt+currentEthStack)
        else:
            basis = buyPrice    

    if ethAmt > 0:
        invested = True
        trailingStopPrice = (1-trailingStopPct)*basis

    return bankroll, ethAmt, invested, basis, trailingStopPrice

def sell(bankroll, invested, ethAmt, stackToSell, sellPrice, basis):
    # Can edit some of this conditionally later for partial sells based on kelly or whatever
    profit = (sellPrice - basis) * stackToSell
    bankroll += (stackToSell*sellPrice)
    invested = False
    profitPercentage = ((stackToSell*sellPrice) / (stackToSell*basis))-1
    basis = 0
    ethAmt -= stackToSell
    return bankroll, profit, profitPercentage, ethAmt, invested, basis

def checkStops(price, basis, trailingPrice, trailingPct):
    #Check the stop, if price is up enough, move the stop price up
    if (price * (1-trailingPct))>trailingPrice:
        stopPrice = price * (1-trailingPct)
    else:
        stopPrice = trailingPct * basis

    takeProfit = 2*basis #100% gain, take it off
    if price >= takeProfit:
        action = "Sell"
    elif price <= stopPrice:
        action = "Sell"
    else:
        action = None

    return action, stopPrice

def convertRowDate(date):
    if row.open_time >= 0:
        date = datetime.fromtimestamp(row.open_time/1000)
        #date = date.strftime("%Y-%m-%d %H:%M:%S")
        date = date.strftime("%Y-%m-%d")
        return date
    else:
        print("Invalid Unix timestamp:", row.open_time)
        return None

if __name__ == '__main__':
    days = 0
    wins = []
    losses = []
    winPct = []
    lossPct = []
    #Put in some global money parameters to be shared by all the functions
    bankroll = 100000
    betSize = 100000 #How much to buy/sell at a time
    ethAmt = 0 #How much ETH we're holding
    invested = False
    basis = 0
    #Probability numbers for the kelly function
    histProb = 0
    trailingStopPrice = 0
    trailingStopPct = .10

    print ("Starting to trade!")
    #print ("Starting bankroll: "+str(bankroll))

    #Test to read 200ma and 50ma
    ethData = session.query(ETHPrice).filter(ETHPrice.ma200 != None).order_by(ETHPrice.open_time).all()

    for row in ethData:
        numberOfBets = len(wins)+len(losses)
        crossover = determine_crossover(row)
        #betSize = max(.33*bankroll, 33000)

        if crossover == "Bullish" and invested:
            #Get the price
            price = row.open
            #IF the price is above a take profit range or below a stop loss, sell it
            action, trailingStopPrice = checkStops(price, basis, trailingStopPrice, trailingStopPct)
            if action == "Sell":
                bankroll, profit, profitPercentage, ethAmt, invested, basis = sell(bankroll, invested, ethAmt, ethAmt, price, basis)
                if profit > 0:
                    wins.append(profit)
                    winPct.append(profitPercentage)
                if profit < 0:
                    losses.append(profit)
                    lossPct.append(profitPercentage)
                date = convertRowDate(row.open_time)
                if date != None:
                    pass
                    #print("Sell at "+"{:.3f}".format(price)+" on "+str(date)+" for a profit/loss of "+"{:.3f}".format(profit)+"\nBankroll: "+"{:.3f}".format(bankroll)+"\n")  
        elif crossover == "Bullish" and not invested:
            #buy 
            price = row.open 
            bankroll, ethAmt, invested, basis, trailingStopPrice = buy(betSize, bankroll, invested, price, basis, ethAmt)
            date = convertRowDate(row.open_time)
            if date != None:
                pass
                #print("Buy at "+"{:.3f}".format(price)+" on "+str(date)+".")
        elif crossover == "Bearish" and invested:
            #sell
            price = row.open
            bankroll, profit, profitPercentage, ethAmt, invested, basis = sell(bankroll, invested, ethAmt, ethAmt, price, basis)
            if profit > 0:
                wins.append(profit)
                winPct.append(profitPercentage)
            if profit < 0:
                losses.append(profit)
                lossPct.append(profitPercentage)
            date = convertRowDate(row.open_time)
            if date != None:
                pass
                #print("Sell at "+"{:.3f}".format(price)+" on "+str(date)+" for a profit/loss of "+"{:.3f}".format(profit)+"\nBankroll: "+"{:.3f}".format(bankroll)+"\n")
        elif crossover == "Bearish" and not invested:
            #Short 
            pass

    print("\nEnd Results\n")
    print("Bankroll: "+str(bankroll))
    ROI = (bankroll / 100000) - 1
    print("ROI: " + "{:.2%}".format(ROI))
    years = 4.25
    aROI = ROI / years
    print("Annualized ROI: "+ "{:.2%}".format(aROI)+"\n")
    print("Number of trades: "+"{:.2f}".format(numberOfBets))
    print("Wins: "+str(round(len(wins),3)))
    print("Losses: "+str(round(len(losses),3)))
    print("\n")
    print("Biggest Win: "+str(round(max(wins))))
    print("Average Win: "+"{:.3f}".format(statistics.mean(wins)))
    print("STDDEV of Wins: "+"{:.3f}".format(statistics.stdev(wins)))
    print("Average Win %: "+"{:.3f}".format(statistics.mean(winPct)))
    print("\n")
    print("Biggest Loss: "+str(round(min(losses))))
    print("Average Loss: "+"{:.3f}".format(statistics.mean((losses))))
    print("STDDEV of losses: "+"{:.3f}".format(statistics.stdev(losses)))
    print("Average Loss %: "+"{:.3f}".format(statistics.mean(lossPct)))

    session.close()