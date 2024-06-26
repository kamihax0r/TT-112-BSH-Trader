import requests
from constants import BASE_URL, LOGIN, PASSWORD

session_token = None

def create_session():
    global session_token
    url = f'{BASE_URL}/sessions'
    payload = {
        'login': LOGIN,
        'password': PASSWORD,
        'remember-me': True
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    session_token = response.json()['data']['session-token']

def get_headers():
    if not session_token:
        create_session()
    return {
        'Authorization': session_token,
        'Content-Type': 'application/json'
    }

def test_connection():
    try:
        response = requests.get(f'{BASE_URL}/customers/me', headers=get_headers())
        response.raise_for_status()
        print(response.json())  # Debugging line
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}
