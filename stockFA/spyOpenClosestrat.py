'''
This is a function that reads the SPY price database and attempts to simulate a strategy of buying the close of each day and selling the open the next morning
'''
from config import logger
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from dbconfig import SPYPrices
from datetime import datetime
import pandas as pd
import statistics
import numpy as np
import scipy.stats as stats
import scipy.optimize as optimize
import sys

# Connect to the database
engine = create_engine('sqlite:///stockdb.db')
Base = declarative_base()

# Create the tables
Base.metadata.create_all(bind=engine)

# Create a session to add data to the database
Session = sessionmaker(bind=engine)
session = Session()

#Create the table query to fit the plan
spyData = pd.read_sql_table('spy_prices',engine)

#Put in some global money parameters to be shared by all the functions
bankroll = 100000
historicWinProb = 0.5480540111199365 #Find this out later
probThreshold = .5155
shares = 0 # Amount of shares on hand
basis = 0 # Track the present cost basis over night

#A Bayesian Kelly Criterion calculator-
def bayesian_kelly_criterion(win_returns, loss_returns, prior_prob):
    # calculate the mean win return and mean loss return
    mean_win = np.mean(win_returns)
    mean_loss = np.mean(loss_returns)

    # calculate the win-loss return ratio
    win_loss_ratio = mean_win / abs(mean_loss)
    
    # update the win probability using Bayes' theorem
    updated_prob = (prior_prob * mean_win) / ((prior_prob * mean_win) + ((1 - prior_prob) * abs(mean_loss)))

    print("Updated Prior: {:.2%}".format(updated_prob))

    # return the bet size as a ratio of the total bankroll
    betSize = updated_prob - (1 - updated_prob) / win_loss_ratio
    
    if betSize < 0:
        betSize = kelly_criterion(historicWinProb)
        print("Mean Win: {:.2%}".format(mean_win))
        print("Mean Loss: {:.2%}".format(mean_loss))
        print("Win/Loss Ratio {:.2%}".format(win_loss_ratio))
        print("Updated Prior: {:.2%}".format(updated_prob))
        print("Bet Size: {:.2%}".format(betSize))
        return updated_prob, betSize
    else:
        return updated_prob,betSize

#The regular KC function, probably best for use with small sample until the bigger set can be trained
#Assume we don't know the win/loss because I'm moving to percentage win/loss and don't have the data yet
def kelly_criterion(win_prob):
    lose_prob = 1 - win_prob
    odds = win_prob/lose_prob
    bet_size = win_prob - (1 - win_prob) / (odds + 1)
    return bet_size
    
def buyStock(betSize, buyprice):
    global bankroll
    global shares
    global basis
    #determine how many shares to buy based on kelly number

    #figure out how many shares (round to whole number?) and the cost basis
    #shares = round(betSize/price)
    shares = betSize/buyprice
    basis = buyprice

    #Pay for the shares
    cash = shares * basis
    bankroll = bankroll - cash
    return
    
def sellStock(price):
    global bankroll
    global basis
    global shares

    cash = shares * price
    bankroll = bankroll + cash

    #Find the percentage profit
    #profit = (price - basis)*shares
    profitPercentage = (price-basis) / basis
 
    #zero out because you sold
    basis = 0
    shares = 0

    #Return the percentage profit to be added to the list
    return profitPercentage

if __name__ == '__main__':
    days = 0
    wins = []
    losses = []
    winprob = historicWinProb
    lossprob = 1-historicWinProb
    kelly = 0
    betSize = 0

    print ("Starting to trade!")
    print ("Starting bankroll: "+str(bankroll))
    stop = range(1, len(spyData))
    #stop = range(1,2500)
    for i in stop:
        today = pd.to_datetime(spyData.iloc[i]['date'])
        yesterday = pd.to_datetime(spyData.iloc[i-1]['date'])
        today_open = spyData.iloc[i]['open']
        today_close = spyData.iloc[i]['close']
        prev_close = spyData.iloc[i-1]['close']
        difference = spyData.iloc[i]['open'] - spyData.iloc[i-1]['close']

        #Get our Kelly Criterion
        if (days<100):
            kelly = kelly_criterion(historicWinProb)
        else:
            winprob,kelly = bayesian_kelly_criterion(wins, losses, winprob)
            if kelly < 0:
                sys.exit("Broke on day "+str(days))
                        
        #If you have shares, sell them at today's open
        if shares>0:
            profitPercentage = sellStock(today_open)
            if profitPercentage > 0:
                wins.append(profitPercentage)
            else:
                losses.append(profitPercentage)

        #Adjust the bet size and update priors
        #betSize = kelly * bankroll
        betSize = bankroll * .33
        print("Making a bet of "+str(betSize)+" based on a kelly of "+str(kelly)+" and a bankroll of "+str(bankroll))

        #We'll use bet size, but buy in round numbers of shares
        #Buy today's lot on close
        if i < len(stop)-1:
            buyStock(betSize, today_close)

        #Increment the day counter
        days=days+1

    print("Final Bankroll: "+"{:.2f}".format(bankroll)+" after "+str(days)+" days")   
    ROI = (bankroll / 100000) - 1
    print("ROI: " + "{:.2%}".format(ROI))
    years = days / 365
    aROI = ROI / years
    print("Annualized ROI: "+ "{:.2%}".format(aROI))
    print("Average Win%: "+"{:.2%}".format(statistics.mean(wins)))
    print("Average Loss%: "+"{:.2%}".format(statistics.mean(losses)))

'''
Some numbers that definitely work, but now we need to use them instead of just spitting them out.
    numWins = len(wins)
    numLosses = len(losses)
    probWin = numWins/days
    probLoss = numLosses/days
    winAmt = sum(wins)
    lossAmt = sum(losses)
    total = winAmt + lossAmt
    mean_wins = statistics.mean(wins)
    mean_losses = statistics.mean(losses)
    stdev_wins = statistics.stdev(wins)
    stdev_losses = statistics.stdev(losses)
'''


