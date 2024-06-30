import requests
from parameters import *
from session_manager import SessionManager
from instruments import Instruments
from datetime import datetime, timedelta, time

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

    def find_112(self, symbol, min_credit, max_credit, min_dte, max_dte):
        try:
            today = datetime.now()
            start_date = today + timedelta(days=min_dte)
            end_date = today + timedelta(days=max_dte)
            dates_to_check = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)]
            
            for exp_date in dates_to_check:
                print(f"Checking expiration date: {exp_date}")
                option_chain = self.instruments.list_future_options(symbol=symbol, expiration_date=exp_date)

                if option_chain and 'data' in option_chain and 'items' in option_chain['data']:
                    options = option_chain['data']['items']
                    long_put = self.find_option_with_delta(options, target_delta=0.25)
                    if long_put:
                        short_put_strike = long_put['strike-price'] - 50
                        short_put = next((opt for opt in options if opt['strike-price'] == short_put_strike and opt['option-type'] == 'put'), None)
                        if short_put:
                            short_put_2 = self.find_option_with_delta(options, target_delta=0.05)
                            if short_put_2:
                                total_credit = short_put_2['ask'] * 2 - (long_put['ask'] - short_put['bid'])
                                print(f"Found potential trade with total credit: {total_credit}")
                                if min_credit <= total_credit <= max_credit:
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
                                    
                                    return {'trade1': trade1, 'trade2': trade2}
                                else:
                                    print(f"Trade credit {total_credit} not within desired range {min_credit} to {max_credit}")
                    else:
                        print(f"No suitable long put found for expiration date: {exp_date}")

            raise ValueError("No suitable expiration found for the 112 trade")
        
        except Exception as e:
            print(f"Error in finding 112 trade: {e}")
            return None
        
    def find_ES_LT112(self):
        return self.find_112("/ES", max_credit=ES_LT112_MAX_CREDIT, min_credit=ES_LT112_MIN_CREDIT, max_dte=ES_LT112_MAX_DTE, min_dte=ES_LT112_MIN_DTE)
           
    def find_ES_standard_112(self):
        return self.find_112("/ES", max_credit=ES_112_MAX_CREDIT, min_credit=ES_112_MIN_CREDIT, max_dte=ES_112_MAX_DTE, min_dte=ES_112_MIN_DTE)
