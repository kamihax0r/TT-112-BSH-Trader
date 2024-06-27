import unittest
from unittest.mock import patch, Mock
from session_manager import SessionManager
from instruments import Instruments

class TestCryptocurrencies(unittest.TestCase):

    def setUp(self):
        self.session_manager = SessionManager()
        self.instruments = Instruments(self.session_manager)
        self.mock_response = Mock()
        self.mock_response.raise_for_status = Mock()
        self.mock_response.json.return_value = {"data": "test"}

    def set_mock(self, mock_get):
        mock_get.return_value = self.mock_response

    # Cryptocurrencies
    @patch.object(SessionManager, 'get_session_token', return_value='mock_token')
    @patch('requests.get')
    def test_list_cryptocurrencies(self, mock_get, mock_session_token):
        self.set_mock(mock_get)
        result = self.instruments.list_cryptocurrencies()
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once_with(
            'https://api.cert.tastyworks.com/instruments/cryptocurrencies',
            headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'}
        )

    @patch.object(SessionManager, 'get_session_token', return_value='mock_token')
    @patch('requests.get')
    def test_get_cryptocurrency(self, mock_get, mock_session_token):
        self.set_mock(mock_get)
        result = self.instruments.get_cryptocurrency('BTC/USD')
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once_with(
            'https://api.cert.tastyworks.com/instruments/cryptocurrencies/BTC/USD',
            headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'}
        )

if __name__ == '__main__':
    unittest.main()
