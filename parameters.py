
# Constants to govern the account level greeks so we can calculate the range we want to stay in and manage risk levels
MAX_DELTA_PCT = .001        #.1% of Net Liquidation Value
MAX_THETA_PCT = .0015       #.15% of Net Liquidation Value
MAX_BUYING_POWER_PCT = .5   #50% of buying power MAX

# Long Term 112 limits
ES_LT112_MAX_CREDIT = 25
ES_LT112_MIN_CREDIT = 20
ES_LT112_MIN_DTE = 95
ES_LT112_MAX_DTE = 120

# Standard 112 Limits
ES_112_MAX_CREDIT = 15
ES_112_MIN_CREDIT = 10 
ES_112_MIN_DTE = 40
ES_112_MAX_DTE = 65