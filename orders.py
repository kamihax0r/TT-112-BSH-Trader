import requests
from constants import BASE_URL
from session_manager import SessionManager

class Orders:
    def __init__(self):
        self.session = SessionManager()

    def margin_requirements_dry_run(self, account_number, order_data):
        url = f'{BASE_URL}/margin/accounts/{account_number}/dry-run'
        response = requests.post(url, headers=self.session.get_headers(), json=order_data)
        response.raise_for_status()
        return response.json()

    # Other order-related functions...
