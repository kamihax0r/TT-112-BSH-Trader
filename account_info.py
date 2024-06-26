import requests
from constants import BASE_URL
from session_manager import get_headers
from datetime import datetime

def get_account_info(account_number):
    url = f'{BASE_URL}/customers/me/accounts/{account_number}'
    try:
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        return response.json().get('data', {})
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

def get_trading_status(account_number):
    url = f'{BASE_URL}/accounts/{account_number}/trading-status'
    try:
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        return response.json().get('data', {})
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

def get_account_positions(account_number):
    url = f'{BASE_URL}/accounts/{account_number}/positions'
    try:
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        return response.json().get('data', {}).get('items', [])
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

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

def get_all_transactions(account_number, params=None):
    url = f'{BASE_URL}/accounts/{account_number}/transactions'
    try:
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json().get('data', {}).get('items', [])
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

def get_transaction_by_id(account_number, transaction_id):
    url = f'{BASE_URL}/accounts/{account_number}/transactions/{transaction_id}'
    try:
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        return response.json().get('data', {})
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

def get_total_fees(account_number, date=None):
    url = f'{BASE_URL}/accounts/{account_number}/transactions/total-fees'
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    params = {'date': date}
    try:
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json().get('data', {})
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}
