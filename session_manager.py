import requests
from constants import BASE_URL, LOGIN, PASSWORD

class SessionManager:
    def __init__(self):
        self.session_token = None

    def create_session(self):
        url = f'{BASE_URL}/sessions'
        payload = {'login': LOGIN, 'password': PASSWORD, 'remember-me': True}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        self.session_token = response.json()['data']['session-token']

    def get_headers(self):
        if not self.session_token:
            self.create_session()
        return {'Authorization': self.session_token, 'Content-Type': 'application/json'}
