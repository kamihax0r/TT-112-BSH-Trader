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
    Import data, clean it up and use only the necessary columns
    '''

    #Import NBA data
    NBAgames = pd.read_csv("NBA_Games2.csv")

    #Split to the 2017 regular season
    NBA_2017_season = NBAgames[(NBAgames['SEASON_ID']==22017) & (NBAgames['GAME_ID']<1000000000)]

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

    #Calculate Pythagorean winPCt
    NBA17['pyth_winPCT'] = NBA17['cumPTS']**2/(NBA17['cumPTS']**2 + NBA17['cumPTSAGN']**2)

    '''
    Now we can apply LPM to our Win/Loss Record
    '''

    #Drop any draws from the data (I don't think there are, but just to be sure)
    #This is our DV variable
    NBA17_WL = NBA17[NBA17['pyth_winPCT'] != 0.5].copy()

    #Run LPM
    reg = smf.ols(formula = 'WIN ~ pyth_winPCT', data = NBA17_WL).fit()
    #print(reg.summary())

    ## Create a scatter plot to explore the relationship between IV (i.e., pyth_wpct) and DV (Win)
    sns.regplot(x = 'pyth_winPCT', y ='WIN', data = NBA17_WL)
    pyplot.xlabel('Pyth. Win%')
    pyplot.ylabel('Win: Binary')
    pyplot.title("Pythagorean Win % and Win-Record", fontsize=20)
    #Uncomment to show the plot
    #pyplot.show()

    '''
    Fit a logistic regression to address issues with Linear Probability Model
    '''
    Win_Pyth = 'WIN~pyth_winPCT'
    model = smf.glm(formula = Win_Pyth, data = NBA17_WL, family=sm.families.Binomial())
    result = model.fit()
    #Uncomment to print values
    '''
    print(result.summary())
    print("Coefficients")
    print(result.params)
    print("p-Values")
    print(result.pvalues)
    print("Dependent variables")
    print(result.model.endog_names)
    print("Number of Observations")
    print(model.nobs)
    '''

    '''
    Obtain the fitted probabilities by using the predict() method
    '''
    fittedProb = result.predict()
    #print(fittedProb[0:10])
    #Convert to win or loss prediction
    fittedWin = [1 if x>.5 else 0 for x in fittedProb]
    #Obtain confusion matrix
    confMatrix = confusion_matrix(NBA17_WL['WIN'], fittedWin)
    # Accessing individual elements in successRate array
    true_negatives = confMatrix[0, 0]
    false_positives = confMatrix[0, 1]
    false_negatives = confMatrix[1, 0]
    true_positives = confMatrix[1, 1]

    successRate = (true_negatives + true_positives) / model.nobs
    #print(successRate)
   #print(classification_report(NBA17_WL['WIN'], fittedWin, digits=3))

    '''
    Use better prediction by incorporating home court advantage
    '''
    Win_Pyth_hm = 'WIN~pyth_winPCT+HOME'
    model2 = smf.glm(formula = Win_Pyth_hm, data = NBA17_WL, family=sm.families.Binomial())
    result2 = model2.fit()
    #print(result2.summary())
    '''
    print("Coefficients")
    print(result2.params)
    print("p-Values")
    print(result2.pvalues)
    print("Dependent variables")
    print(result2.model.endog_names)
    '''

    '''
    Get the fitted probabilities for the new _hm model
    '''
    fittedProb2 = result2.predict()
    #print(fittedProb[0:10])
    #Convert to win or loss prediction
    fittedWin2 = [1 if x>.5 else 0 for x in fittedProb2]
    #Obtain confusion matrix
    confMatrix2 = confusion_matrix(NBA17_WL['WIN'], fittedWin2)
    # Accessing individual elements in successRate array
    true_negatives = confMatrix2[0, 0]
    false_positives = confMatrix2[0, 1]
    false_negatives = confMatrix2[1, 0]
    true_positives = confMatrix2[1, 1]

    successRate2 = (true_negatives + true_positives) / model2.nobs
    #print(successRate2)
    #print(classification_report(NBA17_WL['WIN'], fittedWin2, digits=3))
