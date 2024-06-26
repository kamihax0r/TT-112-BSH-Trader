import requests
from constants import BASE_URL
from session_manager import get_headers

def get_current_positions():
    url = f'{BASE_URL}/accounts/me/positions'
    try:
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        return response.json().get('data', {}).get('items', [])
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}
