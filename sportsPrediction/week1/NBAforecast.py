import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as pyplot
import seaborn as sns

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report

import statsmodels.formula.api as smf
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.iolib.summary2 import summary_col



matplotlib.use('TkAgg')

if __name__ == '__main__':

    '''
    Import data, clean it up and use only the necessary columns
    '''

    #Import NBA data
    NBAgames = pd.read_csv("NBA_Games2.csv")

    print(NBAgames)
    pass
    
    #Filter rows for 2017 season
    NBA_2017_season = NBAgames[(NBAgames['SEASON_ID']==22017) & (NBAgames['GAME_ID']<1000000000)].copy()
    
    #Define the variables
    NBA17 = NBA_2017_season[['GAME_ID', 'MATCHUP', 'PTS', 'PLUS_MINUS', 'WIN']]

    #Break MATCHUP column into team, opponent, and home_away dummy variable
    NBA17 = NBA17.copy()
    NBA17[['TEAM', 'OPPONENT']] = NBA17['MATCHUP'].str.split(' vs\. | @', expand=True).copy()
    NBA17.loc[NBA17['MATCHUP'].str.contains('vs'), 'home'] = 1
    NBA17.loc[NBA17['MATCHUP'].str.contains('@'), 'home'] = 0
    #Make the dummy var
    homedummy = pd.get_dummies(NBA17['home'], prefix='home_away')
    #Merge in the dummies
    NBA17 = pd.concat([NBA17,homedummy], axis=1)
    #Drop the old column
    NBA17 = NBA17.drop('home', axis=1)
    NBA17 = NBA17.drop('home_away_1.0', axis=1)
    #Clean up the column name
    NBA17 = NBA17.rename(columns={'home_away_0.0':'HOME'})

    '''
    Cleaned up data set is ready to calculate Pythagorean win pct
    '''
    #Get points against
    #PTS_AGAINST = PTS - PLUS_MINUS
    NBA17['PTSAGN'] = NBA17['PTS'] - NBA17['PLUS_MINUS']
    NBA17['PTSAGN'] = NBA17['PTSAGN'].astype(int)

    #Order the data set by game ID
    NBA17 = NBA17.sort_values(by='GAME_ID')    

    #Calculate cumulative PTS and PTS_AGAINST
    NBA17['cumPTS'] = NBA17.groupby('TEAM',group_keys=False)['PTS'].apply(lambda x: x.cumsum())
    NBA17['cumPTSAGN'] = NBA17.groupby('TEAM',group_keys=False)['PTSAGN'].apply(lambda x: x.cumsum())

    '''
    Now the data set is ready to split, so we need to get test and train datasets
    Train = GAME_ID <= 21700615 
    Test = GAME_ID > 21700615
    '''
    NBA17pre = NBA17[NBA17['GAME_ID']<=21700615].copy()
    NBA17post = NBA17[NBA17['GAME_ID']>21700615].copy()

    #Team level data set
    NBA17train = NBA17pre.groupby('TEAM')[['WIN', 'PTS', 'PTSAGN']].sum()
    NBA17test = NBA17post.groupby('TEAM')[['WIN', 'PTS', 'PTSAGN']].sum()

    '''
    Set up the training data set
    '''
    #Find the total number of games
    NBA17train_gameNum = NBA17pre.groupby('TEAM').size().reset_index(name='GAMES')
    #Merge back into the data set
    NBA17train = pd.merge(NBA17train, NBA17train_gameNum, on=('TEAM'))
    #Calculate Pythagorean winPCT
    NBA17train['pyth_winPCT_pre'] = NBA17train['PTS']**2 / (NBA17train['PTS']**2 + NBA17train['PTSAGN']**2)
    NBA17train['winPCT_pre'] = NBA17train['WIN'] / NBA17train['GAMES']

    #Check the correlation
    correlation = NBA17train['pyth_winPCT_pre'].corr(NBA17train['winPCT_pre'])
    print(correlation)


    '''
    Set up the test data set
    '''
    #Find the total number of games
    NBA17test_gameNum = NBA17post.groupby('TEAM').size().reset_index(name='GAMES')
    #Merge back into test data set
    NBA17test = pd.merge(NBA17test, NBA17test_gameNum, on=('TEAM'))
    #Calculate winPCT and pyth_winPCT
    NBA17test['pyth_winPCT_post'] = NBA17test['PTS']**2 / (NBA17test['PTS']**2 + NBA17test['PTSAGN']**2)
    NBA17test['winPCT_post'] = NBA17test['WIN'] / NBA17test['GAMES']

    '''
    Merge the data sets together to prepare to do forecast
    '''
    NBA17 = pd.merge(NBA17test, NBA17train, on='TEAM')

    #Plot the winPCT pre with post
    sns.regplot(x='winPCT_pre', y='winPCT_post', data=NBA17,  marker='.')
    pyplot.xlabel('1st half win%')
    pyplot.ylabel('2nd half win%')
    pyplot.title("Correlation: Pre-win% vs Post-win%", fontsize=15)
    #pyplot.show()

    #Linear Model
    WinPct_lm = smf.ols(formula = 'winPCT_post ~ winPCT_pre', data=NBA17).fit()
    #print(WinPct_lm.summary())

    #Plot pyth_winPCT
    sns.regplot(x='pyth_winPCT_pre', y='winPCT_post', data=NBA17,  marker='.')
    pyplot.xlabel('1st half Pyth.win%')
    pyplot.ylabel('2nd half win%')
    pyplot.title("Correlation: Pre-Pyth.win% vs Post-win%", fontsize=15)
    #pyplot.show()

    #Linear Model with pyth_winPCT
    PythWin_lm = smf.ols(formula = 'winPCT_post ~ pyth_winPCT_pre', data=NBA17).fit()
    #print(PythWin_lm.summary())

    '''
    Combine the models and compare their results
    '''
    info_dict={'R-squared' : lambda x: f"{x.rsquared:.2f}"}
    Header = ['1','2']
    Table_1 = summary_col([WinPct_lm, PythWin_lm,],\
                        regressor_order=['Intercept','Win%','Pyth.Win%'], model_names = Header, info_dict=info_dict)
    #print(Table_1)