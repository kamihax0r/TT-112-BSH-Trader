import requests
from constants import BASE_URL, get_headers

class Orders:
    def __init__(self):
        pass

    def search_orders(self, account_number, start_date=None, end_date=None, underlying_symbol=None, status=None, sort='Desc', per_page=10, page_offset=0):
        url = f'{BASE_URL}/accounts/{account_number}/orders'
        params = {
            'start-date': start_date,
            'end-date': end_date,
            'underlying-symbol': underlying_symbol,
            'status': status,
            'sort': sort,
            'per-page': per_page,
            'page-offset': page_offset
        }
        try:
            response = requests.get(url, headers=get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def get_todays_orders(self, account_number):
        url = f'{BASE_URL}/accounts/{account_number}/orders/live'
        try:
            response = requests.get(url, headers=get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def create_leg(self, action, symbol, quantity, instrument_type):
        return {
            "action": action,
            "symbol": symbol,
            "quantity": quantity,
            "instrument-type": instrument_type
        }

    def create_order(self, time_in_force, order_type, price=None, price_effect=None, stop_trigger=None, value=None, value_effect=None, legs=[]):
        order = {
            "time-in-force": time_in_force,
            "order-type": order_type,
            "legs": legs
        }

        if price:
            order["price"] = price
            order["price-effect"] = price_effect

        if stop_trigger:
            order["stop-trigger"] = stop_trigger

        if value:
            order["value"] = value
            order["value-effect"] = value_effect

        return order

    def add_leg(self, order, leg):
        order["legs"].append(leg)
        return order

    def validate_order(self, order):
        if order["order-type"] in ["Limit", "Stop Limit"] and ("price" not in order or "price-effect" not in order):
            return False, "Limit and Stop Limit orders require 'price' and 'price-effect'."
        if order["order-type"] in ["Stop", "Stop Limit"] and "stop-trigger" not in order:
            return False, "Stop and Stop Limit orders require 'stop-trigger'."
        if order["order-type"] == "Notional Market" and ("value" not in order or "value-effect" not in order):
            return False, "Notional Market orders require 'value' and 'value-effect'."
        return True, "Order is valid."

    def example_orders(self):
        example_market_order = self.create_order(
            time_in_force="Day",
            order_type="Market",
            legs=[self.create_leg(action="Buy to Open", symbol="AAPL", quantity=1, instrument_type="Equity")]
        )

        example_limit_order = self.create_order(
            time_in_force="Day",
            order_type="Limit",
            price=5.0,
            price_effect="Debit",
            legs=[self.create_leg(action="Buy to Open", symbol="AAPL", quantity=100, instrument_type="Equity")]
        )

        return {
            "example_market_order": example_market_order,
            "example_limit_order": example_limit_order
        }

    def validate_complex_order(self, complex_order):
        required_fields = ["type", "orders"]
        for field in required_fields:
            if field not in complex_order:
                return False, f"Missing required field '{field}' in complex order."

        if complex_order["type"] == "OTOCO":
            if "trigger-order" not in complex_order:
                return False, "OTOCO complex orders require a 'trigger-order'."
            is_valid, message = self.validate_order(complex_order["trigger-order"])
            if not is_valid:
                return False, f"Invalid trigger order: {message}"

        for order in complex_order["orders"]:
            is_valid, message = self.validate_order(order)
            if not is_valid:
                return False, f"Invalid order in complex orders: {message}"

        return True, "Complex order is valid."

    def submit_order(self, account_number, order_data):
        is_valid, message = self.validate_order(order_data)
        if not is_valid:
            return {'error': message}
        url = f'{BASE_URL}/accounts/{account_number}/orders'
        try:
            response = requests.post(url, headers=get_headers(), json=order_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def submit_order_dryrun(self, account_number, order_data):
        is_valid, message = self.validate_order(order_data)
        if not is_valid:
            return {'error': message}
        url = f'{BASE_URL}/accounts/{account_number}/orders/dry-run'
        try:
            response = requests.post(url, headers=get_headers(), json=order_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def cancel_order(self, account_number, order_id):
        url = f'{BASE_URL}/accounts/{account_number}/orders/{order_id}'
        try:
            response = requests.delete(url, headers=get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def cancel_replace_order(self, account_number, order_id, new_order_data):
        is_valid, message = self.validate_order(new_order_data)
        if not is_valid:
            return {'error': message}
        url = f'{BASE_URL}/accounts/{account_number}/orders/{order_id}'
        try:
            response = requests.put(url, headers=get_headers(), json=new_order_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def submit_complex_order(self, account_number, complex_order_data):
        is_valid, message = self.validate_complex_order(complex_order_data)
        if not is_valid:
            return {'error': message}
        url = f'{BASE_URL}/accounts/{account_number}/complex-orders'
        try:
            response = requests.post(url, headers=get_headers(), json=complex_order_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def cancel_complex_order(self, account_number, complex_order_id):
        url = f'{BASE_URL}/accounts/{account_number}/complex-orders/{complex_order_id}'
        try:
            response = requests.delete(url, headers=get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def margin_dry_run(self, account_number, order_data):
        url = f'{BASE_URL}/margin/accounts/{account_number}/dry-run'
        try:
            response = requests.post(url, headers=get_headers(), json=order_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
