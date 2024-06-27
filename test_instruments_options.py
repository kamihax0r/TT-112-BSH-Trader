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

    @patch.object(SessionManager, 'get_session_token', return_value='mock_token')
    @patch('requests.get')
    def test_list_active_equities(self, mock_get, mock_session_token):
        self.set_mock(mock_get)
        result = self.instruments.list_active_equities()
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once_with(
            'https://api.cert.tastyworks.com/instruments/equities/active',
            headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'},
            params={'lendability': None, 'per-page': 1000, 'page-offset': 0}
        )

    @patch.object(SessionManager, 'get_session_token', return_value='mock_token')
    @patch('requests.get')
    def test_get_equity(self, mock_get, mock_session_token):
        self.set_mock(mock_get)
        result = self.instruments.get_equity('AAPL')
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once_with(
            'https://api.cert.tastyworks.com/instruments/equities/AAPL',
            headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'}
        )

    # Equity Options
    @patch.object(SessionManager, 'get_session_token', return_value='mock_token')
    @patch('requests.get')
    def test_list_nested_option_chains(self, mock_get, mock_session_token):
        self.set_mock(mock_get)
        result = self.instruments.list_nested_option_chains('AAPL')
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once_with(
            'https://api.cert.tastyworks.com/option-chains/AAPL/nested',
            headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'}
        )

    @patch.object(SessionManager, 'get_session_token', return_value='mock_token')
    @patch('requests.get')
    def test_list_detailed_option_chains(self, mock_get, mock_session_token):
        self.set_mock(mock_get)
        result = self.instruments.list_detailed_option_chains('AAPL')
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once_with(
            'https://api.cert.tastyworks.com/option-chains/AAPL',
            headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'}
        )

    @patch.object(SessionManager, 'get_session_token', return_value='mock_token')
    @patch('requests.get')
    def test_list_compact_option_chains(self, mock_get, mock_session_token):
        self.set_mock(mock_get)
        result = self.instruments.list_compact_option_chains('AAPL')
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once_with(
            'https://api.cert.tastyworks.com/option-chains/AAPL/compact',
            headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'}
        )

    @patch.object(SessionManager, 'get_session_token', return_value='mock_token')
    @patch('requests.get')
    def test_list_equity_options(self, mock_get, mock_session_token):
        self.set_mock(mock_get)
        result = self.instruments.list_equity_options()
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once_with(
            'https://api.cert.tastyworks.com/instruments/equity-options',
            headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'},
            params={'symbol[]': None, 'active': None, 'with-expired': None}
        )

    @patch.object(SessionManager, 'get_session_token', return_value='mock_token')
    @patch('requests.get')
    def test_get_equity_option(self, mock_get, mock_session_token):
        self.set_mock(mock_get)
        result = self.instruments.get_equity_option('AAPL')
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once_with(
            'https://api.cert.tastyworks.com/instruments/equity-options/AAPL',
            headers={'Authorization': 'mock_token', 'Content-Type': 'application/json'}
        )

if __name__ == '__main__':
    unittest.main()
