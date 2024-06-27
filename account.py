import requests
from constants import BASE_URL 

class Account:
    def __init__(self, account_number, session_manager):
        self.account_number = account_number
        self.session_manager = session_manager
        self.session_manager = session_manager
        self.info = {}
        self.trading_status = {}
        self.positions = []
        self.balance = {}
        self.greeks = {'delta': 0, 'theta': 0, 'vega': 0, 'gamma': 0}
        self.greeks = {'delta': 0, 'theta': 0, 'vega': 0, 'gamma': 0}

    def get_info(self):
        url = f'{BASE_URL}/customers/me/accounts/{self.account_number}'
        headers = self.session_manager.get_headers()
        headers = self.session_manager.get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        self.info = response.json().get('data', {})
        return self.info

    def get_trading_status(self):
        url = f'{BASE_URL}/accounts/{self.account_number}/trading-status'
        headers = self.session_manager.get_headers()
        headers = self.session_manager.get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        self.trading_status = response.json().get('data', {})
        return self.trading_status

    def get_positions(self):
        url = f'{BASE_URL}/accounts/{self.account_number}/positions'
        headers = self.session_manager.get_headers()
        headers = self.session_manager.get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        self.positions = response.json().get('data', {}).get('items', [])
        return self.positions

    def get_balance(self):
        url = f'{BASE_URL}/accounts/{self.account_number}/balances'
        headers = self.session_manager.get_headers()
        headers = self.session_manager.get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        self.balance = response.json().get('data', {})
        return self.balance

    def get_account_greeks(self):
        self.get_positions()
        self.greeks = {'delta': 0, 'theta': 0, 'vega': 0, 'gamma': 0}
        for pos in self.positions:
            if 'greeks' in pos:
                self.greeks['delta'] += pos['greeks'].get('delta', 0)
                self.greeks['theta'] += pos['greeks'].get('theta', 0)
                self.greeks['vega'] += pos['greeks'].get('vega', 0)
                self.greeks['gamma'] += pos['greeks'].get('gamma', 0)
        return self.greeks
    def get_account_greeks(self):
        self.get_positions()
        self.greeks = {'delta': 0, 'theta': 0, 'vega': 0, 'gamma': 0}
        for pos in self.positions:
            if 'greeks' in pos:
                self.greeks['delta'] += pos['greeks'].get('delta', 0)
                self.greeks['theta'] += pos['greeks'].get('theta', 0)
                self.greeks['vega'] += pos['greeks'].get('vega', 0)
                self.greeks['gamma'] += pos['greeks'].get('gamma', 0)
        return self.greeks
