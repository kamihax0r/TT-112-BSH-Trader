import pandas as pd
import numpy as np
import matplotlib.pyplot as plot
import seaborn as sns
import statsmodels.formula.api as smf

from bevel.linear_ordinal_regression import OrderedLogit as ol
#Ordered Logit Documentation
#https://github.com/Shopify/bevel

import warnings

if __name__ == '__main__':

    '''
    Data Preparation Stage
    '''
    #Read in the data
    table = pd.read_excel("Bundy Data.xlsx")

    #Assign predition of H-home win, D-draw, and A-away win
    #B365res - Bet 365 result predicted
    table['B365res'] ='' #initialize with an empty string
       
    for index,row in table.iterrows():
        #Grab the values
        homeOdds = row['B365H']
        drawOdds = row['B365D']
        awayOdds = row['B365A']

        #Assign the outcome
        if homeOdds < drawOdds and homeOdds<awayOdds:
            table.at[index,'B365res'] = 'H'
        elif awayOdds<homeOdds and awayOdds<drawOdds:
            table.at[index,'B365res'] = 'A'
        else:
            table.at[index,'B365res'] = 'D'

    #Assign the winValue points
    table['winValue'] = np.where(table['FTR']=='H',2,(np.where(table['FTR']=='D',1,0)))

    #Compare the B365 accuracy to the leage result using a cross tab
    cross = pd.crosstab(table['FTR'], table['B365res'], dropna=True)

    #print(cross)

    #Create the log of the ratios between TMhome and TMaway data
    table['logTMratio'] = np.log(table['Tmhome']/table['Tmaway'])

    '''
    Estimate a logit model of home team wins depending on the log TMvalue ratio, using the data for games 1 to 224  as the “training data”
    '''
    #Grab the training set
    firstHalfData = table[:223]
    #Run ordered logit regression of winValue on TMratio
    from bevel.linear_ordinal_regression import OrderedLogit
    ol = OrderedLogit()
    ol.fit(firstHalfData['logTMratio'],firstHalfData['winValue'])
    #ol.print_summary()

    '''
    We want to convert our estimates into probabilities, and to do this we need the estimates of the intercepts as well. 
    The coefficient for logTMratio is stored as ol.coef_[0], while the threshold between A and D is stored as ol.coef_[1] the threshold between D and H is stored as ol.coef_[2] 
    We can print these out with appropriate names:
    '''
    #Get the coefficient and the intercepts between away/draw and draw/home
    beta = ol.coef_[0]
    interceptAD = ol.coef_[1]
    interceptDH = ol.coef_[2]

    '''
    To generate the forecast probabilities we need to manipulate the coefficients. 
    The logit regression equation has the form log(p/(1-p)) = a + bX. 
    By rearranging this equation we can obtain p = 1/(1+ exp(a +bX)).

    For each game, we know X (logTMratio) and now we know beta. 
    Since this is an ordered logit with three possible outcomes, the probability of the worst outcome A (viewed by the home team) depends on intercept_AD (ol.coef_[1]), the probability of the middle outcome D depends on intercept_AD and intercept_DH (ol.coef_[1] and ol.coef_[2]), while the probability of the best outcome depends on intercept_DH.
    If we calculate the probability of A first, using ol.coef_[0] and ol.coef_[1], then when calculating the probability of D we can use the fact that we already have the probability of A, and also when calculating the probability of H we can use the fact that we already have the probability of D.
    Thus, we now create the predicted values of the H, A and D probabilities from our model. 
    We can create a prediction for every game in the season, so we now apply the formulas to the whole dataframe, not the season19 df that we used to generate the regression estimates:

    Define the predicted probabilities and the predicted results, using the entire data set
    '''
    warnings.filterwarnings("ignore")
    x = table['logTMratio']
    #Reverse the logit regression equation to obtain the formula for the probability of H/D/A
    table['probA'] = 1 / (1 + np.exp(-(interceptAD - beta * x)))
    table['probD'] = 1/(1+np.exp(-(interceptDH-beta*x))) - table['probA']
    table['probH'] = 1 - table['probA'] - table['probD']
    warnings.filterwarnings("default")

    #Figure out which one has the highest probability
    table['maxProb'] = table[['probA','probD','probH']].max(axis=1)
    #Assign H or A to the highest prop
    table['logitProb']=np.where(table['maxProb']==table['probA'],'A',np.where(table['maxProb']==table['probD'],'D','H'))
    #Create a field that is true if the logitProb matches the real result and false otherwise
    table['logitTrue']=np.where(table['logitProb']==table['FTR'],1,0)

    #Create dummy variables for home/away/draw 
    table['Houtcome'] = np.where(table['FTR']=='H',1,0)
    table['Doutcome'] = np.where(table['FTR']=='D',1,0)
    table['Aoutcome'] = np.where(table['FTR']=='A',1,0)

    #Create dummy values for the B365 predictions
    table['B365Houtcome'] = np.where(table['B365res']=='H',1,0)
    table['B365Doutcome'] = np.where(table['B365res']=='D',1,0)
    table['B365Aoutcome'] = np.where(table['B365res']=='A',1,0)

    #Create the B365 probabilities for each outcome H/D/A
    '''
    Now we derive the bookmaker probabilities from the betting odds. The outcome probability equals 1/(decimal odds). 
    However, if you make this calculation and sum the three possibilities the total is greater than one. 
    This is called the 'overround', or the 'vig' - and represents the profit of the bookmaker. 
    To calculate the implied probability from the betting odds you have to divide by the sum of the three numbers, so that your final probabilities add up to 1 (100%).
    '''
    table['B365HPr']= 1/(table['B365H'])/(1/(table['B365H'])+ 1/(table['B365D'])+ 1/(table['B365A']))
    table['B365DPr']= 1/(table['B365D'])/(1/(table['B365H'])+ 1/(table['B365D'])+ 1/(table['B365A']))
    table['B365APr']= 1/(table['B365A'])/(1/(table['B365H'])+ 1/(table['B365D'])+ 1/(table['B365A']))


    '''
    For games played from May 2020, compare the bookmaker probabilities and model probabilities in terms of the mean number of successfully predicted outcomes and the Brier scores.
    '''
    #Create a variable that is true if B365 made the right prediction and false otherwise
    table['B365true'] = np.where(table['FTR']==table['B365res'],1,0)

    #Grab the second half of the season, games from May onward
    secondHalfData = table[224:].copy()

    #Regression success rate
    secondHalfData['logitTrue'].mean()
    #B365success rate
    secondHalfData['B365true'].mean()

    #print(secondHalfData['logitTrue'].mean())

    #Calculate the TM Brier score, where predicted is 
    BrierLogit = ((secondHalfData['probH'] - secondHalfData['Houtcome'])**2 +(secondHalfData['probD'] - secondHalfData['Doutcome'])**2 + (secondHalfData['probA'] - secondHalfData['Aoutcome'])**2).sum()/(len(secondHalfData))
    BrierB365 = ((secondHalfData['B365HPr'] - secondHalfData['Houtcome'])**2 +(secondHalfData['B365DPr'] - secondHalfData['Doutcome'])**2 + (secondHalfData['B365APr'] - secondHalfData['Aoutcome'])**2).sum()/(len(secondHalfData))

    BrierLogitMean = np.mean(BrierLogit)
    BrierB365Mean = np.mean(BrierB365)

    print(BrierB365Mean)
    print(BrierLogitMean)
