import requests
from constants import BASE_URL, LOGIN, PASSWORD

class SessionManager:
    def __init__(self):
        self.session_token = None

    def create_session(self):
        url = f'{BASE_URL}/sessions'
        data = {
            'login': LOGIN,
            'password': PASSWORD
        }
        response = requests.post(url, json=data)
        if response.status_code == 401:
            raise Exception(f"Authentication failed: {response.json().get('error', 'Unknown error')}")
        response.raise_for_status()
        self.session_token = response.json()['data']['session-token']

    def get_session_token(self):
        if not self.session_token:
            self.create_session()
        return self.session_token

    def get_headers(self):
        session_token = self.get_session_token()
        return {
            'Authorization': f'{session_token}',
            'Content-Type': 'application/json'
        }

    def test_connection(self):
        headers = self.get_headers()
        url = f'{BASE_URL}/sessions/validate'
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            return {'error': '401 Unauthorized. Invalid session token.'}
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            return {'error': str(e)}
