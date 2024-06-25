import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as pyplot
import seaborn as sns
import statsmodels.formula.api as smf

from sklearn.linear_model import LogisticRegression
import statsmodels.api as sm
import statsmodels.formula.api as smf

from sklearn.metrics import confusion_matrix, classification_report

matplotlib.use('TkAgg')

if __name__ == '__main__':

    '''
    Data imports and data setup
    '''

    #Import NBA data
    NBAgames = pd.read_excel("NBA_data_week4.xlsx")

    #Get Home and Away Win Probabilities as function of bookmaker odds
    NBAgames['Hwinprob']= 1/(NBAgames['hwinodds'])/(1/(NBAgames['hwinodds'])+ 1/(NBAgames['hloseodds']))
    #Subtract from 1 to get away win prob, since there are not ties
    NBAgames['Awinprob']=1-NBAgames['Hwinprob']

    #Not sure why we're setting it to 1 if the Home team loses
    NBAgames['Hloss']=np.where(NBAgames['homepts']<NBAgames['vispts'],1,0)
    NBAgames['Winner']=np.where(NBAgames['homepts']>NBAgames['vispts'], 'H','A')

    #Make predictions based on bookmaker odds
    #Home win if home win odds >.5
    NBAgames['BookPred'] = np.where(NBAgames['Hwinprob']>.5,'H','A')

    #Make a variable that is the log of the ratio of the home salary to the away salary
    NBAgames['logSalRatio'] = np.log(NBAgames['hteamsal']/NBAgames['opposal'])

    '''
    Fit a logistic regression of the log ratio of salary onto Home win for all games
    '''
    hwinFit = 'hwin~logSalRatio'
    model = smf.glm(formula = hwinFit, data = NBAgames, family=sm.families.Binomial())
    result = model.fit()

    #Uncomment to print values
    #print("Logistic Regression of logSalRatio on hwin for all games\n")
    #print(result.summary(),"\n")

    #2018 data (training set)
    NBAgames2018 = NBAgames[NBAgames['year']==2018].copy()

    print("\n")
    print("Games in 2018: ",len(NBAgames2018),"\n")

    #2019 data
    NBAgames2019 = NBAgames[NBAgames['year']==2019].copy()

    '''
    Fit a logistic regression of the log ratio of salary onto Home win for 2018 games
    '''
    hwinFit = 'hwin~logSalRatio'
    model = smf.glm(formula = hwinFit, data = NBAgames2018, family=sm.families.Binomial())
    result = model.fit()

    #Uncomment to print values
    print("Logistic Regression of logSalRatio on hwin for games in 2018\n")
    print(result.summary(),"\n")

    '''
    Obtain the fitted probabilities by using the predict() method
    '''
    fittedProb2019 = result.predict(NBAgames2019)
    #Convert to win or loss prediction
    fittedWin2019 = [1 if x>.5 else 0 for x in fittedProb2019]
    #Attach the Fitted Win Predictions back to the main dataframe, assign H if it predicts home (1) and A if it predicts away (0)
    NBAgames2019['LogitHwinProb'] = fittedProb2019
    NBAgames2019['LogitHwin']= fittedWin2019
    NBAgames2019['LogitCorrect'] = np.where(NBAgames2019['LogitHwin']==NBAgames2019['hwin'],1,0)
    #Check the bookmaker correctness
    NBAgames2019['BookHwin'] = np.where(NBAgames2019['BookPred']=='H',1,0) 
    NBAgames2019['BookCorrect'] = np.where(NBAgames2019['BookHwin']==NBAgames2019['hwin'],1,0)
    #Get the means for the bookie being correct and the logit regression being correct
    BookCorrMean = NBAgames2019['BookCorrect'].mean()
    LogitCorrMean = NBAgames2019['LogitCorrect'].mean()    

    print("Book Prediction Success Rate: ",BookCorrMean,"\n")
    print("Logit Prediction Success Rate: ",LogitCorrMean,"\n")

    #Get the Brier scores for each
    #Two outcome Brier score looks like this: NBA19['Brier']= (NBA19['win']-NBA19['winprob'])**2 + ((1-NBA19['win'])-(1-NBA19['winprob']))**2

    NBAgames2019['BrierLogit'] = ((NBAgames2019['hwin']-NBAgames2019['LogitHwinProb']))**2 + ((1-NBAgames2019['hwin'])-(1-NBAgames2019['LogitHwinProb']))**2
    NBAgames2019['BrierBook'] = ((NBAgames2019['hwin']-NBAgames2019['Hwinprob']))**2 + ((1-NBAgames2019['hwin'])-(1-NBAgames2019['Hwinprob']))**2
    BookBrierMean = NBAgames2019['BrierBook'].mean()
    LogitBrierMean = NBAgames2019['BrierLogit'].mean()

    print("Book Brier Score: ",BookBrierMean)
    print("Regression Model Brier Score: ",LogitBrierMean,"\n")


