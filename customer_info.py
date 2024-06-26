import requests
from session_manager import SessionManager
from constants import BASE_URL

class CustomerInfo:
    def __init__(self):
        self.session = SessionManager()

    def get_customer_info(self):
        url = f'{BASE_URL}/customers/me'
        headers = self.session.get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['data']

    def get_acct_numbers(self):
        url = f'{BASE_URL}/customers/me/accounts'
        headers = self.session.get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        accounts_data = response.json()['data']['items']
        return [account['account']['account-number'] for account in accounts_data]

    def get_session_token(self):
        return self.session.get_session_token()
