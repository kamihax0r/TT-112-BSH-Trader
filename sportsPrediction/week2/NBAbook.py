# install the packages we need

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == '__main__':
    # load the data
    NBA19 = pd.read_excel("NBA2019odds.xlsx")
    #print(NBA19.head(10))

    #Get Win Probabilities as function of bookmaker odds
    NBA19['winprob']= 1/(NBA19['winodds'])/(1/(NBA19['winodds'])+ 1/(NBA19['loseodds']))

    #Get team level data set
    NBAteamprob = NBA19.groupby('team')[['winprob','win']].mean()

    #Plot the relationship between winning probability and winning outcomes
    sns.relplot(x="winprob", y="win", data = NBAteamprob, s=30)
    #plt.show()

    #Compute the correlations (quite high :D)
    correlation = np.corrcoef(NBAteamprob["winprob"], NBAteamprob['win'])
    #print(correlation)

    #Drop away games
    NBA19 = NBA19.drop(NBA19[NBA19['home']==0].index)

    #print(NBA19)

    '''
    Create different data subsets for comparison

    a.  One for games where the absolute value of the points difference is less than 9 and another for games where the points difference is greater than 9 (9 is the median points difference in the data)
    b.	One for games that went to overtime, and one for games which finished in regulation time
    c.	One for games played in calendar year 2018, one for games played in calendar year 2019
    d.	One for each month in the data (October to April)

    '''

    # Split data based on point difference
    greater_than_9 = NBA19[NBA19['diff'].abs() > 9]
    less_than_9 = NBA19[NBA19['diff'].abs() < 9]

    # Split data based on overtime
    overtime_games = NBA19[NBA19['overtime'] == 1]
    non_overtime_games = NBA19[NBA19['overtime'] == 0]

    # Split based on 2018/2019 year
    games_2018 = NBA19[NBA19['year'] == 2018]
    games_2019 = NBA19[NBA19['year'] == 2019]

    # Split based on calendar months
    month_data = pd.DataFrame()
    for m in NBA19['month'].unique():
        currMonth = NBA19[NBA19['month'] == m].copy()
        month_data = pd.concat([month_data,currMonth])
    # Reset the index
    month_data.reset_index(drop=True, inplace=True)

    '''
    Here is the code to answer the quiz questions
    '''

    #1.
    #What is the correlation between the home team win probability and home team wins across the entire 2018/19 season? 
    corr1819 = np.corrcoef(NBA19['winprob'], NBA19['win'])
    print(f"Answer 1: {corr1819}\n")

    # 2.
    # What is the correlation between the home team win probability and home team wins for games where the points difference was less than 9?
    corrUnder9 = np.corrcoef(less_than_9['winprob'], less_than_9['win'])
    print(f"Answer 2: {corrUnder9}\n")

    # 3.
    # What is the correlation between the home team win probability and home team wins for games where the points difference was greater than 9?
    corrOver9 = np.corrcoef(greater_than_9['winprob'], greater_than_9['win'])
    print(f"Answer 3: {corrOver9}\n")

    # 4.
    # Considering the answers to the last two questions, what do you think is the most likely explanation of these results
    
    # 5.
    # What is the correlation between the home team win probability and home team wins for games where the game went to overtime?
    corrOT = np.corrcoef(overtime_games['winprob'], overtime_games['win'])
    print(f"Answer 5: {corrOT}\n")

    # 6.
    # What is the correlation between the home team win probability and home team wins for games where the game was finished in regular time?
    corrNonOT = np.corrcoef(non_overtime_games['winprob'], non_overtime_games['win'])
    print(f"Answer 6: {corrNonOT}\n")

    # 7.
    # What is the correlation between the home team win probability and home team wins for games where the game was played in calendar year 2018?
    corr2018 = np.corrcoef(games_2018['winprob'], games_2018['win'])
    print(f"Answer 7: {corr2018}\n")

    # 8.
    # What is the correlation between the home team win probability and home team wins for games where the game was played in calendar year 2019?
    corr2019 = np.corrcoef(games_2019['winprob'], games_2019['win'])
    print(f"Answer 8: {corr2019}\n")

    # 9.
    # In which month was the correlation coefficient between the home team win probability and home team wins greatest?
    # 10.
    # In which month was the correlation coefficient between the home team win probability and home team wins lowest?
    print("Printing correlations for each month\n\n")
    for m in month_data['month'].unique():
        currMonth = month_data[month_data['month']==m]
        corrCurrMonth = np.corrcoef(currMonth['winprob'], currMonth['win'])
        print(f"Correlation for month {m}: {corrCurrMonth}\n\n")