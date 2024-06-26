import requests
from constants import BASE_URL
from session_manager import get_headers

def get_customer_info():
    url = f'{BASE_URL}/customers/me'
    try:
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        customer_data = response.json()['data']
        
        customer_info = {
            'first_name': customer_data.get('first-name'),
            'last_name': customer_data.get('last-name'),
            'email': customer_data.get('email'),
            'address': customer_data.get('address'),
            'birth_date': customer_data.get('birth-date'),
            'mobile_phone_number': customer_data.get('mobile-phone-number'),
            'permitted_account_types': customer_data.get('permitted-account-types'),
        }
        return customer_info
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

def get_acctNumbers():
    url = f'{BASE_URL}/customers/me/accounts'
    try:
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        accounts_data = response.json()['data']['items']
        
        # Collecting all account numbers
        if accounts_data:
            account_numbers = [account['account']['account-number'] for account in accounts_data]
            return account_numbers
        else:
            return {'error': 'No accounts found'}
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}
