import requests
from constants import *
from session_manager import SessionManager
from instruments import Instruments
from datetime import datetime, time

class TradeFinder:
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.instruments = Instruments(session_manager)
        
    def is_market_open():
        now = datetime.now().time()
        market_open = time(9, 30)
        market_close = time(16, 0)
        return market_open <= now <= market_close    

    def find_option_with_delta(self, options, target_delta):
        closest_option = min(options, key=lambda x: abs(x['greeks']['delta'] - target_delta))
        return closest_option

    def find_option_with_price(self, options, target_price):
        closest_option = min(options, key=lambda x: abs(x['ask'] - target_price))
        return closest_option

    def find_112(self, symbol, DTE=120):
        try:
            if symbol.startswith("/"):
                option_chains = self.instruments.list_detailed_futures_option_chains(symbol)
            else:
                option_chains = self.instruments.list_detailed_option_chains(symbol)

            # Debug print the option chains response
            #print(f"Option chains for {symbol}: {option_chains}")

            expiration_dates = option_chains['data']['items']
            expiration_dates.sort(key=lambda x: abs((datetime.strptime(x['expiration-date'], '%Y-%m-%d') - datetime.now()).days - DTE))

            # Debug check for the expiration dates, it might be easier just to look from today + MIN to today + MAX
            print(f"Expiration dates: {expiration_dates}")
            
            for exp_date in expiration_dates:
                print(f"Date: {exp_date}")

            ''' 
            for exp_date in expiration_dates:
                print(f"Checking expiration date: {exp_date['expiration-date']}")
                options_chain = next((chain for chain in option_chains['data']['items'] if chain['expiration-date'] == exp_date['expiration-date']), None)
                
                if options_chain and 'options' in options_chain:
                    options = options_chain['options']
                    long_put = self.find_option_with_delta(options, target_delta=0.25)

                    if long_put:
                        short_put_strike = long_put['strike-price'] - 50
                        short_put = next((opt for opt in options if opt['strike-price'] == short_put_strike and opt['option-type'] == 'put'), None)
                        if short_put:
                            nearest_expiration = exp_date
                            break
                else:
                    print(f"No options found for expiration date: {exp_date['expiration-date']}")

            if not nearest_expiration:
                raise ValueError("No suitable expiration found for the 112 trade")

            options_chain = next((chain for chain in option_chains['data']['items'] if chain['expiration-date'] == nearest_expiration['expiration-date']), None)
            options = options_chain['options']
            long_put = self.find_option_with_delta(options, target_delta=0.25)
            short_put = next((opt for opt in options if opt['strike-price'] == long_put['strike-price'] - 50 and opt['option-type'] == 'put'), None)
            short_put_2 = self.find_option_with_delta(options, target_delta=0.05)

            trade1 = {
                'order_type': 'Complex',
                'time_in_force': 'GTC',
                'price': 0,
                'price_effect': 'Debit',
                'legs': [
                    {"action": "BUY_TO_OPEN", "symbol": long_put['symbol'], "quantity": 1},
                    {"action": "SELL_TO_OPEN", "symbol": short_put['symbol'], "quantity": 1}
                ]
            }

            trade2 = {
                'order_type': 'Complex',
                'time_in_force': 'GTC',
                'price': 0,
                'price_effect': 'Credit',
                'legs': [
                    {"action": "SELL_TO_OPEN", "symbol": short_put_2['symbol'], "quantity": 2}
                ]
            }

            #print(f"Trade 1: {trade1}")
            #print(f"Trade 2: {trade2}")
            
            return {'trade1': trade1, 'trade2': trade2}
            '''
            return None
        
        except Exception as e:
            print(f"Error in finding 112 trade: {e}")
            return None

    def find_ES_LT112(self):
        min_credit = ES_LT112_MIN_CREDIT
        max_credit = ES_LT112_MAX_CREDIT
        try:
            for dte in range(ES_LT112_MIN_DTE, ES_LT112_MAX_DTE + 1):
                print(f"Checking for DTE: {dte}")
                es_trade = self.find_112("/ES", DTE=dte)
                
                if es_trade:
                    print(f"Trade found for DTE {dte}: {es_trade}")
                    trade1_price = es_trade['trade1'].get('price', 0)
                    trade2_price = es_trade['trade2'].get('price', 0)
                    total_credit = trade2_price - trade1_price
                    print(f"Total credit for the trade: {total_credit}")

                    if self.is_market_open():
                        if min_credit <= total_credit <= max_credit:
                            print("Suitable trade found within the desired credit range.")
                            return es_trade
                        else:
                            print("Trade does not meet the credit requirements.")
                    else:
                        print("Market is closed. Skipping price checking logic.")
                        return es_trade

            print("No suitable 112 trade found within the desired credit range and DTE")
            return None

        except Exception as e:
            print(f"Error in finding standard 112 trade: {e}")
            return None
        
    def find_ES_standard_112(self):
        min_credit = ES_112_MIN_CREDIT
        max_credit = ES_112_MAX_CREDIT
        try:
            for dte in range(ES_112_MIN_DTE, ES_112_MAX_DTE + 1):
                es_trade = self.find_112("/ES", DTE=dte)
                
                if es_trade:
                    total_credit = es_trade['trade2']['price'] - es_trade['trade1']['price']
                    if min_credit <= total_credit <= max_credit:
                        return es_trade

            print("No suitable 112 trade found within the desired credit range and DTE")
            return None

        except Exception as e:
            print(f"Error in finding standard 112 trade: {e}")
            return None
