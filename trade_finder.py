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

    def find_112(self, symbol, max_credit, min_credit, max_dte, min_dte):
        try:
            expiration_dates = []
            for dte in range(min_dte, max_dte + 1):
                exp_date = datetime.now() + timedelta(days=dte)
                expiration_dates.append(exp_date.strftime('%Y-%m-%d'))
            
            suitable_trades = []

            for exp_date in expiration_dates:
                print(f"Checking expiration date: {exp_date}")
                if symbol.startswith("/"):
                    options_chain = self.instruments.list_detailed_futures_option_chains(symbol, expiration=exp_date)
                else:
                    options_chain = self.instruments.list_detailed_option_chains(symbol, expiration=exp_date)
                
                if options_chain and 'options' in options_chain:
                    options = options_chain['options']
                    long_put = self.find_option_with_delta(options, target_delta=0.25)

                    if long_put:
                        short_put_strike = long_put['strike-price'] - 50
                        short_put = next((opt for opt in options if opt['strike-price'] == short_put_strike and opt['option-type'] == 'put'), None)
                        if short_put:
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

                            total_credit = trade2['price'] - trade1['price']
                            if min_credit <= total_credit <= max_credit:
                                suitable_trades.append({'trade1': trade1, 'trade2': trade2, 'credit': total_credit})
            
            if suitable_trades:
                best_trade = max(suitable_trades, key=lambda x: x['credit'])
                return best_trade
            else:
                print("No suitable 112 trade found within the desired credit range and DTE")
                return None

        except Exception as e:
            print(f"Error in finding 112 trade: {e}")
            return None

    def find_ES_LT112(self):
        return self.find_112("/ES", max_credit=ES_LT112_MAX_CREDIT, min_credit=ES_LT112_MIN_CREDIT, max_dte=ES_LT112_MAX_DTE, min_dte=ES_LT112_MIN_DTE)
           
    def find_ES_standard_112(self):
        return self.find_112("/ES", max_credit=ES_112_MAX_CREDIT, min_credit=ES_112_MIN_CREDIT, max_dte=ES_112_MAX_DTE, min_dte=ES_112_MIN_DTE)
