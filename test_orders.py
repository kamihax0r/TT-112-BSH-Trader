import unittest
from unittest.mock import patch, Mock
from orders import Orders
from session_manager import SessionManager
from constants import BASE_URL

class TestOrders(unittest.TestCase):

    def setUp(self):
        self.session_manager = SessionManager()
        self.orders = Orders(self.session_manager)

    @patch('orders.requests.get')
    def test_search_orders(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'test'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with patch.object(SessionManager, 'get_headers', return_value={'Authorization': 'mock_token', 'Content-Type': 'application/json'}):
            result = self.orders.search_orders('account_number')
            self.assertEqual(result, {'data': 'test'})
            mock_get.assert_called_once_with(
                f'{BASE_URL}/accounts/account_number/orders',
                headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'},
                params={
                    'start-date': None,
                    'end-date': None,
                    'underlying-symbol': None,
                    'status': None,
                    'sort': 'Desc',
                    'per-page': 10,
                    'page-offset': 0
                }
            )

    @patch('orders.requests.get')
    def test_get_todays_orders(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'test'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        with patch.object(SessionManager, 'get_headers', return_value={'Authorization': 'mock_token', 'Content-Type': 'application/json'}):
            result = self.orders.get_todays_orders('account_number')
            self.assertEqual(result, {'data': 'test'})
            mock_get.assert_called_once_with(
                f'{BASE_URL}/accounts/account_number/orders/live',
                headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'}
            )

    @patch('orders.requests.post')
    def test_submit_order(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'test'}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        order_data = {'order-type': 'Market'}
        with patch.object(SessionManager, 'get_headers', return_value={'Authorization': 'mock_token', 'Content-Type': 'application/json'}):
            result = self.orders.submit_order('account_number', order_data)
            self.assertEqual(result, {'data': 'test'})
            mock_post.assert_called_once_with(
                f'{BASE_URL}/accounts/account_number/orders',
                headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'},
                json=order_data
            )

    @patch('orders.requests.post')
    def test_submit_order_dryrun(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'test'}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        order_data = {'order-type': 'Market'}
        with patch.object(SessionManager, 'get_headers', return_value={'Authorization': 'mock_token', 'Content-Type': 'application/json'}):
            result = self.orders.submit_order_dryrun('account_number', order_data)
            self.assertEqual(result, {'data': 'test'})
            mock_post.assert_called_once_with(
                f'{BASE_URL}/accounts/account_number/orders/dry-run',
                headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'},
                json=order_data
            )

    @patch('orders.requests.delete')
    def test_cancel_order(self, mock_delete):
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'test'}
        mock_response.raise_for_status = Mock()
        mock_delete.return_value = mock_response

        with patch.object(SessionManager, 'get_headers', return_value={'Authorization': 'mock_token', 'Content-Type': 'application/json'}):
            result = self.orders.cancel_order('account_number', 'order_id')
            self.assertEqual(result, {'data': 'test'})
            mock_delete.assert_called_once_with(
                f'{BASE_URL}/accounts/account_number/orders/order_id',
                headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'}
            )

    @patch('orders.requests.put')
    def test_cancel_replace_order(self, mock_put):
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'test'}
        mock_response.raise_for_status = Mock()
        mock_put.return_value = mock_response

        new_order_data = {'order-type': 'Market'}
        with patch.object(SessionManager, 'get_headers', return_value={'Authorization': 'mock_token', 'Content-Type': 'application/json'}):
            result = self.orders.cancel_replace_order('account_number', 'order_id', new_order_data)
            self.assertEqual(result, {'data': 'test'})
            mock_put.assert_called_once_with(
                f'{BASE_URL}/accounts/account_number/orders/order_id',
                headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'},
                json=new_order_data
            )

    @patch('orders.requests.post')
    def test_submit_complex_order(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'test'}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        complex_order_data = {
            'type': 'OTOCO',
            'trigger-order': {'order-type': 'Market'},
            'orders': [{'order-type': 'Limit', 'price': '100', 'price-effect': 'Debit'}]
        }
        with patch.object(SessionManager, 'get_headers', return_value={'Authorization': 'mock_token', 'Content-Type': 'application/json'}):
            result = self.orders.submit_complex_order('account_number', complex_order_data)
            self.assertEqual(result, {'data': 'test'})
            mock_post.assert_called_once_with(
                f'{BASE_URL}/accounts/account_number/complex-orders',
                headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'},
                json=complex_order_data
            )

        
    @patch('orders.requests.delete')
    def test_cancel_complex_order(self, mock_delete):
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'test'}
        mock_response.raise_for_status = Mock()
        mock_delete.return_value = mock_response

        with patch.object(SessionManager, 'get_headers', return_value={'Authorization': 'mock_token', 'Content-Type': 'application/json'}):
            result = self.orders.cancel_complex_order('account_number', 'complex_order_id')
            self.assertEqual(result, {'data': 'test'})
            mock_delete.assert_called_once_with(
                f'{BASE_URL}/accounts/account_number/complex-orders/complex_order_id',
                headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'}
            )

    @patch('orders.requests.post')
    def test_margin_dry_run(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'test'}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        order_data = {'order-type': 'Market'}
        with patch.object(SessionManager, 'get_headers', return_value={'Authorization': 'mock_token', 'Content-Type': 'application/json'}):
            result = self.orders.margin_dry_run('account_number', order_data)
            self.assertEqual(result, {'data': 'test'})
            mock_post.assert_called_once_with(
                f'{BASE_URL}/margin/accounts/account_number/dry-run',
                headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'},
                json=order_data
            )

if __name__ == '__main__':
    unittest.main()
