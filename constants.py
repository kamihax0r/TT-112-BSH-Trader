import os

LOGIN = 'login'
PASSWORD = 'password'
BASE_URL = 'https://api.cert.tastyworks.com'
STREAMER_URL = 'wss://streamer.cert.tastyworks.com'




"""
# Determine if the environment is testing or production
#ENVIRONMENT = os.getenv('ENVIRONMENT', 'production').lower()
ENVIRONMENT = 'testing'

# Set base URL based on environment
if ENVIRONMENT == 'testing':
    #TEST Credentials
    LOGIN = 'kamihax0rsandbox'
    PASSWORD = '$u@Dk968W$aQbe6Q'
    BASE_URL = 'https://api.cert.tastyworks.com'
    STREAMER_URL = 'wss://streamer.cert.tastyworks.com'

else:
    #Production Account Credentials
    BASE_URL = 'https://api.tastyworks.com'
    LOGIN = 'prod_login'
    PASSWORD = 'prod_password'
    STREAMER_URL = 'wss://streamer.tastyworks.com'
    
"""
