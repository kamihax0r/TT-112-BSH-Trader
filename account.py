import requests
from session_manager import SessionManager
from constants import BASE_URL
from datetime import datetime

class Account:
    def __init__(self, account_number):
        self.account_number = account_number
        self.session = SessionManager()
        self.info = {}
        self.trading_status = {}
        self.positions = []
        self.balance = {}

    def get_info(self):
        url = f'{BASE_URL}/customers/me/accounts/{self.account_number}'
        headers = self.session.get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        self.info = response.json().get('data', {})
        return self.info

    def get_trading_status(self):
        url = f'{BASE_URL}/accounts/{self.account_number}/trading-status'
        headers = self.session.get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        self.trading_status = response.json().get('data', {})
        return self.trading_status

    def get_positions(self):
        url = f'{BASE_URL}/accounts/{self.account_number}/positions'
        headers = self.session.get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        self.positions = response.json().get('data', {}).get('items', [])
        return self.positions

    def get_balance(self):
        url = f'{BASE_URL}/accounts/{self.account_number}/balances'
        headers = self.session.get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        self.balance = response.json().get('data', {})
        return self.balance

    def get_transactions(self, start_date=None, end_date=None, params=None):
        url = f'{BASE_URL}/accounts/{self.account_number}/transactions'
        headers = self.session.get_headers()
        
        if params is None:
            params = {}
        
        if start_date:
            params['start-date'] = start_date
        if end_date:
            params['end-date'] = end_date
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get('data', {}).get('items', [])

    def get_transaction_by_id(self, transaction_id):
        url = f'{BASE_URL}/accounts/{self.account_number}/transactions/{transaction_id}'
        headers = self.session.get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('data', {})

    def get_total_fees(self, date=None):
        url = f'{BASE_URL}/accounts/{self.account_number}/transactions/total-fees'
        headers = self.session.get_headers()
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        params = {'date': date}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get('data', {})
