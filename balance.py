import requests
from constants import BASE_URL
from session_manager import get_headers

def get_account_balance(account_number):
    url = f'{BASE_URL}/accounts/{account_number}/balances'
    try:
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        return response.json().get('data', {})
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

def get_all_balances(account_numbers):
    balances = {}
    for account_number in account_numbers:
        balance = get_account_balance(account_number)
        if 'error' in balance:
            balances[account_number] = {'error': balance['error']}
        else:
            balances[account_number] = balance
    return balances