import unittest
from unittest.mock import patch, Mock
from session_manager import SessionManager
from instruments import Instruments

class TestInstruments(unittest.TestCase):

    def setUp(self):
        self.session_manager = SessionManager()
        self.instruments = Instruments(self.session_manager)
        self.mock_response = Mock()
        self.mock_response.raise_for_status = Mock()
        self.mock_response.json.return_value = {"data": "test"}

    def set_mock(self, mock_get):
        mock_get.return_value = self.mock_response

    # Equities
    @patch.object(SessionManager, 'get_session_token', return_value='mock_token')
    @patch('requests.get')
    def test_list_equities(self, mock_get, mock_session_token):
        self.set_mock(mock_get)
        result = self.instruments.list_equities()
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once_with(
            'https://api.cert.tastyworks.com/instruments/equities',
            headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'},
            params={'symbol[]': None, 'lendability': None, 'is-index': None, 'is-etf': None}
        )

    # Futures
    @patch.object(SessionManager, 'get_session_token', return_value='mock_token')
    @patch('requests.get')
    def test_list_futures(self, mock_get, mock_session_token):
        self.set_mock(mock_get)
        result = self.instruments.list_futures()
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once_with(
            'https://api.cert.tastyworks.com/instruments/futures',
            headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'},
            params={'symbol[]': None, 'product-code[]': None}
        )

    @patch.object(SessionManager, 'get_session_token', return_value='mock_token')
    @patch('requests.get')
    def test_get_future(self, mock_get, mock_session_token):
        self.set_mock(mock_get)
        result = self.instruments.get_future('ESZ2')
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once_with(
            'https://api.cert.tastyworks.com/instruments/futures/ESZ2',
            headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'}
        )

    @patch.object(SessionManager, 'get_session_token', return_value='mock_token')
    @patch('requests.get')
    def test_list_future_products(self, mock_get, mock_session_token):
        self.set_mock(mock_get)
        result = self.instruments.list_future_products()
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once_with(
            'https://api.cert.tastyworks.com/instruments/future-products',
            headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'}
        )

    @patch.object(SessionManager, 'get_session_token', return_value='mock_token')
    @patch('requests.get')
    def test_get_future_product(self, mock_get, mock_session_token):
        self.set_mock(mock_get)
        result = self.instruments.get_future_product('CME', 'ES')
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once_with(
            'https://api.cert.tastyworks.com/instruments/future-products/CME/ES',
            headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'}
        )

if __name__ == '__main__':
    unittest.main()
