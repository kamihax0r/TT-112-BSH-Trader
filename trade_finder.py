import requests
from constants import *
from session_manager import SessionManager
from instruments import Instruments
from datetime import datetime

class TradeFinder:
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.instruments = Instruments(session_manager)

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
                
            expiration_dates = option_chains['data']['items']
            expiration_dates.sort(key=lambda x: abs((datetime.strptime(x['expiration-date'], '%Y-%m-%d') - datetime.now()).days - DTE))

            nearest_expiration = None
            for exp_date in expiration_dates:
                options = next((chain for chain in option_chains['data']['items'] if chain['expiration-date'] == exp_date['expiration-date']), None)
                long_put = self.find_option_with_delta(options['options'], target_delta=0.25)

                if long_put:
                    short_put_strike = long_put['strike-price'] - 50
                    short_put = next((opt for opt in options['options'] if opt['strike-price'] == short_put_strike and opt['type'] == 'put'), None)
                    if short_put:
                        nearest_expiration = exp_date
                        break

            if not nearest_expiration:
                raise ValueError("No suitable expiration found for the 112 trade")

            options = next((chain for chain in option_chains['data']['items'] if chain['expiration-date'] == nearest_expiration['expiration-date']), None)
            long_put = self.find_option_with_delta(options['options'], target_delta=0.25)
            short_put = next((opt for opt in options['options'] if opt['strike-price'] == long_put['strike-price'] - 50 and opt['type'] == 'put'), None)
            short_put_2 = self.find_option_with_delta(options['options'], target_delta=0.05)

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

            print(f"Trade 1: {trade1}")
            print(f"Trade 2: {trade2}")
            
            return {'trade1': trade1, 'trade2': trade2}

        except Exception as e:
            print(f"Error in finding 112 trade: {e}")
            return None

    def find_ES_LT112(self):
        min_credit = ES_LT112_MIN_CREDIT
        max_credit = ES_LT112_MAX_CREDIT
        try:
            for dte in range(ES_LT112_MIN_DTE, ES_LT112_MAX_DTE + 1):
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
