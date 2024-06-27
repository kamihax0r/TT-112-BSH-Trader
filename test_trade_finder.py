import unittest
from unittest.mock import patch
from trade_finder import TradeFinder
from session_manager import SessionManager
from orders import Orders
from account import Account
from customer_info import CustomerInfo

class TestTradeFinder(unittest.TestCase):

    def setUp(self):
        self.session_manager = SessionManager()
        self.trade_finder = TradeFinder(self.session_manager)
        self.orders = Orders(self.session_manager)
        self.customer_info = CustomerInfo(self.session_manager.get_headers())

    @patch('trade_finder.TradeFinder.find_ES_112')
    @patch('orders.Orders.submit_order')
    def test_find_ES_112_and_place_trade(self, mock_submit_order, mock_find_ES_112):
        # Mock the response of find_ES_112
        mock_find_ES_112.return_value = {
            'trade1': {
                'legs': [
                    {"action": "BUY_TO_OPEN", "symbol": "ESU21_20210917_3700P", "quantity": 1},
                    {"action": "SELL_TO_OPEN", "symbol": "ESU21_20210917_3650P", "quantity": 1}
                ]
            },
            'trade2': {
                'legs': [
                    {"action": "SELL_TO_OPEN", "symbol": "ESU21_20210917_3500P", "quantity": 2}
                ]
            }
        }

        # Mock the response of submit_order
        mock_submit_order.return_value = {'data': 'test'}

        # Call find_ES_112 and get trades
        trades = self.trade_finder.find_ES_112()
        self.assertIn('trade1', trades)
        self.assertIn('trade2', trades)

        # Fetch account numbers using CustomerInfo class
        account_numbers = self.customer_info.get_acct_numbers()

        # Ensure we have at least one account number
        self.assertTrue(len(account_numbers) > 0)

        # Use the first account number for testing
        account_number = account_numbers[0]

        # Submit the trades to the sandbox account
        for trade_name, trade in trades.items():
            order_data = {
                'order_type': 'Complex',
                'time_in_force': 'GTC',
                'price': 0,
                'price_effect': 'Debit',
                'legs': trade['legs']
            }
            response = self.orders.submit_order(account_number, order_data)
            print(f"Submitted {trade_name}: {response}")  # Add logging
            self.assertEqual(response, {'data': 'test'})

        # Fetch positions for the account and check if the trades are placed
        account = Account(account_number, self.session_manager)
        positions = account.get_positions()
        print(f"Positions for account {account_number}: {positions}")  # Add logging
        self.assertTrue(len(positions) > 0)

if __name__ == '__main__':
    unittest.main()
