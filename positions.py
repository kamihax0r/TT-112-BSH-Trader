import requests
from constants import BASE_URL
from session_manager import SessionManager

class Positions:
    def __init__(self):
        self.session = SessionManager()

    def get_account_margin_requirements(self, account_number):
        url = f'{BASE_URL}/margin/accounts/{account_number}/requirements'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    # Other position-related functions...

    def list_positions(self, account_number):
        url = f'{BASE_URL}/accounts/{account_number}/positions'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    def get_position(self, account_number, position_id):
        url = f'{BASE_URL}/accounts/{account_number}/positions/{position_id}'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()
