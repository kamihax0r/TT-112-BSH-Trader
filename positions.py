import requests
from constants import BASE_URL

class Positions:
    def __init__(self, session_manager):
        self.session_manager = session_manager

    def list_positions(self, account_number):
        url = f'{BASE_URL}/accounts/{account_number}/positions'
        headers = self.session_manager.get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['data']

    def get_account_margin_requirements(self, account_number):
        url = f'{BASE_URL}/accounts/{account_number}/margin'
        headers = self.session_manager.get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['data']
