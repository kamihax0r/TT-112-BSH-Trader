import requests
from session_manager import SessionManager
from constants import BASE_URL

class ConnectionTest:
    def __init__(self):
        self.session = SessionManager()

    def test_connection(self):
        url = f'{BASE_URL}/test-connection-endpoint'
        headers = self.session.get_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
