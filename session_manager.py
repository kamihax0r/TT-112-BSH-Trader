import requests
from constants import BASE_URL, USERNAME, PASSWORD

class SessionManager:
    def __init__(self):
        self.session_token = None
        self.login()

    def login(self):
        url = f'{BASE_URL}/sessions'
        response = requests.post(url, json={"login": USERNAME, "password": PASSWORD})
        response.raise_for_status()
        self.session_token = response.json()['data']['session-token']

    def get_headers(self):
        return {"Authorization": f"Bearer {self.session_token}"}

    def get_session_token(self):
        return self.session_token
