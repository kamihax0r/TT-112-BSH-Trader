import requests
from constants import BASE_URL

class CustomerInfo:
    def __init__(self, headers):
        self.headers = headers

    def get_customer_info(self):
        url = f'{BASE_URL}/customers/me'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()['data']

    def get_acct_numbers(self):
        url = f'{BASE_URL}/customers/me/accounts'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        accounts_data = response.json()['data']['items']
        return [account['account']['account-number'] for account in accounts_data]
