import requests
from constants import BASE_URL
from session_manager import SessionManager

class Instruments:
    def __init__(self, session_manager: SessionManager):
        self.session = session_manager

    # Equities
    def list_equities(self, symbols=None, lendability=None, is_index=None, is_etf=None):
        url = f'{BASE_URL}/instruments/equities'
        params = {
            'symbol[]': symbols,
            'lendability': lendability,
            'is-index': is_index,
            'is-etf': is_etf
        }
        response = requests.get(url, headers=self.session.get_headers(), params=params)
        response.raise_for_status()
        return response.json()

    def list_active_equities(self, lendability=None, per_page=1000, page_offset=0):
        url = f'{BASE_URL}/instruments/equities/active'
        params = {
            'lendability': lendability,
            'per-page': per_page,
            'page-offset': page_offset
        }
        response = requests.get(url, headers=self.session.get_headers(), params=params)
        response.raise_for_status()
        return response.json()

    def get_equity(self, symbol):
        url = f'{BASE_URL}/instruments/equities/{symbol}'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    # Equity Options
    def list_nested_option_chains(self, underlying_symbol):
        url = f'{BASE_URL}/option-chains/{underlying_symbol}/nested'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    def list_detailed_option_chains(self, underlying_symbol):
        url = f'{BASE_URL}/option-chains/{underlying_symbol}'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    def list_compact_option_chains(self, underlying_symbol):
        url = f'{BASE_URL}/option-chains/{underlying_symbol}/compact'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    def list_equity_options(self, symbols=None, active=None, with_expired=None):
        url = f'{BASE_URL}/instruments/equity-options'
        params = {
            'symbol[]': symbols,
            'active': active,
            'with-expired': with_expired
        }
        response = requests.get(url, headers=self.session.get_headers(), params=params)
        response.raise_for_status()
        return response.json()

    def get_equity_option(self, symbol):
        url = f'{BASE_URL}/instruments/equity-options/{symbol}'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    # Futures
    def list_futures(self, symbols=None, product_codes=None):
        url = f'{BASE_URL}/instruments/futures'
        params = {
            'symbol[]': symbols,
            'product-code[]': product_codes
        }
        response = requests.get(url, headers=self.session.get_headers(), params=params)
        response.raise_for_status()
        return response.json()

    def get_future(self, symbol):
        url = f'{BASE_URL}/instruments/futures/{symbol}'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    def list_future_products(self):
        url = f'{BASE_URL}/instruments/future-products'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    def get_future_product(self, exchange, code):
        url = f'{BASE_URL}/instruments/future-products/{exchange}/{code}'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    # Future Options
    def list_nested_futures_option_chains(self, product_code):
        url = f'{BASE_URL}/futures-option-chains/{product_code}/nested'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    def list_detailed_futures_option_chains(self, product_code):
        url = f'{BASE_URL}/futures-option-chains/{product_code}'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    def list_future_options(self, symbols=None, option_root_symbol=None, expiration_date=None, option_type=None, strike_price=None):
        url = f'{BASE_URL}/instruments/future-options'
        params = {
            'symbol[]': symbols,
            'option-root-symbol': option_root_symbol,
            'expiration-date': expiration_date,
            'option-type': option_type,
            'strike-price': strike_price
        }
        response = requests.get(url, headers=self.session.get_headers(), params=params)
        response.raise_for_status()
        return response.json()

    def get_future_option(self, symbol):
        url = f'{BASE_URL}/instruments/future-options/{symbol}'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    def list_future_option_products(self):
        url = f'{BASE_URL}/instruments/future-option-products'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    def get_future_option_product(self, exchange, root_symbol):
        url = f'{BASE_URL}/instruments/future-option-products/{exchange}/{root_symbol}'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    # Cryptocurrencies
    def list_cryptocurrencies(self):
        url = f'{BASE_URL}/instruments/cryptocurrencies'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    def get_cryptocurrency(self, symbol):
        url = f'{BASE_URL}/instruments/cryptocurrencies/{symbol}'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    # Warrants
    def list_warrants(self, symbols=None):
        url = f'{BASE_URL}/instruments/warrants'
        params = {
            'symbol[]': symbols
        }
        response = requests.get(url, headers=self.session.get_headers(), params=params)
        response.raise_for_status()
        return response.json()

    def get_warrant(self, symbol):
        url = f'{BASE_URL}/instruments/warrants/{symbol}'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()

    # Quantity Decimal Precisions
    def list_quantity_decimal_precisions(self):
        url = f'{BASE_URL}/instruments/quantity-decimal-precisions'
        response = requests.get(url, headers=self.session.get_headers())
        response.raise_for_status()
        return response.json()
