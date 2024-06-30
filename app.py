from flask import Flask, jsonify, request
from session_manager import SessionManager
from customer_info import CustomerInfo
from orders import Orders
from streamer import Streamer
from account import Account
from instruments import Instruments
from greeks_review import GreeksReview
from trade_finder import TradeFinder
from datetime import datetime
import logging
import requests


app = Flask(__name__)

# Initialize global variables
session_manager = SessionManager()
session_manager.create_session()
headers = session_manager.get_headers()

# Initialize the app
account_positions = {}
account_balances = {}
accounts = []  # Initialize the global accounts list

trade_finder = TradeFinder(session_manager)
# Initialize orders
orders_info = Orders(session_manager)
instruments = Instruments(session_manager)

# Initialize the customer info
customer_info = CustomerInfo(headers)
# Fetch account numbers
account_numbers = customer_info.get_acct_numbers()
# Initialize Greeks review
greeks_review = GreeksReview(accounts)
# Initialize and start the streamer
streamer = Streamer(session_manager, account_numbers)
streamer.start()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def initialize_app():
    global orders_info, customer_info, account_positions, account_balances, accounts, streamer, instruments, greeks_review, trade_finder, session_manager
    try:
        # Fetch positions and balances for all accounts and store them
        for account_number in account_numbers:
            account = Account(account_number, session_manager)
            positions = account.get_positions()
            balance = account.get_balance()
            account_positions[account_number] = positions
            account_balances[account_number] = balance
            accounts.append(account)
        return
    
    except Exception as e:
        print(f"Error during initialization: {e}")

@app.route('/', methods=['GET'])
def home():
    return 'Welcome to the Tastytrade API Flask app!'

@app.route('/test-connection', methods=['POST'])
def test_connection_route():
    result = session_manager.test_connection()
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

@app.route('/account-numbers', methods=['GET'])
def account_numbers_route():
    global customer_info
    if not customer_info:
        return jsonify({'error': 'Customer info instance not initialized'}), 500

    try:
        account_numbers = customer_info.get_acct_numbers()
        return jsonify({'account_numbers': account_numbers})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/positions', methods=['GET'])
def positions_route():
    global accounts
    positions_data = {}
    if not accounts:
        return jsonify({'error': 'No accounts found'}), 500
    try:
        for account in accounts:
            positions_data[account.account_number] = account.get_positions()
        return jsonify({'positions': positions_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/balances', methods=['GET'])
def balances_route():
    global accounts
    balances_data = {}
    if not accounts:
        return jsonify({'error': 'No accounts found'}), 500
    try:
        for account in accounts:
            balances_data[account.account_number] = account.get_balance()
        return jsonify({'balances': balances_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/account-greeks/<account_number>', methods=['GET'])
def account_greeks_route(account_number):
    global accounts
    account = next((acc for acc in accounts if acc.account_number == account_number), None)
    if not account:
        return jsonify({'error': f'Account {account_number} not found'}), 404

    try:
        greeks = account.get_account_greeks()
        return jsonify({'account_greeks': greeks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/account-greeks', methods=['GET'])
def all_accounts_greeks_route():
    global accounts
    if not accounts:
        return jsonify({'error': 'Accounts not initialized'}), 500

    try:
        account_greeks = {}
        for account in accounts:
            greeks = account.get_account_greeks()
            account_greeks[account.account_number] = greeks
        return jsonify({'account_greeks': account_greeks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/orders/<account_number>', methods=['GET'])
def get_orders_route(account_number):
    global orders_info
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    underlying_symbol = request.args.get('underlying_symbol')
    status = request.args.get('status')
    sort = request.args.get('sort', 'Desc')
    per_page = request.args.get('per_page', 10)
    page_offset = request.args.get('page_offset', 0)

    try:
        orders = orders_info.search_orders(account_number, start_date, end_date, underlying_symbol, status, sort, per_page, page_offset)
        return jsonify({'orders': orders})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/orders/<account_number>/<order_id>', methods=['GET'])
def get_order_by_id_route(account_number, order_id):
    global orders_info
    try:
        orders = orders_info.search_orders(account_number)
        order = next((order for order in orders['data']['items'] if order['order-id'] == order_id), None)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        return jsonify({'order': order})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/orders/all', methods=['GET'])
def get_all_orders_route():
    global customer_info, orders_info
    if not customer_info:
        return jsonify({'error': 'Customer info instance not initialized'}), 500

    try:
        account_numbers = customer_info.get_acct_numbers()
        all_orders = {}
        for account_number in account_numbers:
            orders = orders_info.search_orders(account_number)
            all_orders[account_number] = orders
        return jsonify({'all_orders': all_orders})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recommendations', methods=['GET'])
def recommendations_route():
    global trading_logic
    if not trading_logic:
        return jsonify({'error': 'Trading logic not initialized'}), 500

    try:
        recommendations = trading_logic.analyze_and_trade()
        return jsonify({'recommendations': recommendations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/review-greeks', methods=['GET'])
def review_greeks_route():
    global greeks_review
    if not greeks_review:
        return jsonify({'error': 'Greeks review not initialized'}), 500

    try:
        review_results = greeks_review.review_greeks()
        return jsonify({'greeks_review': review_results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/find-and-place-ES-LT112', methods=['POST'])
def find_and_place_ES_LT112():
    global trade_finder, orders
    
    if not trade_finder or not orders:
        return jsonify({"error": "TradeFinder or Orders instance not initialized"}), 500
    
    es_trade = trade_finder.find_ES_LT112()
    
    if es_trade:
        # Place both trades
        order_ids = []
        for trade in [es_trade['trade1'], es_trade['trade2']]:
            response = orders.place_order(trade)
            if response.status_code == 200:
                order_id = response.json()['data']['order_id']
                order_ids.append(order_id)
            else:
                return jsonify({"error": "Failed to place trade", "details": response.json()}), 500
        
        return jsonify({"order_ids": order_ids}), 200
    else:
        return jsonify({"error": "No suitable 112 trade found"}), 400

@app.route('/nested-futures-options-chains', methods=['GET'])
def get_nested_futures_options_chains():
    global instruments, session_manager
    print(f"Auth Token Inside Our Endpoint: {session_manager.get_session_token()}")
    if not instruments:
        instruments = Instruments(session_manager)
    try:
        symbol = "/ES"
        expiration_date = request.args.get('expiration_date')  # Assuming the expiration date is passed as a query parameter
        if not expiration_date:
            return jsonify({'error': 'Expiration date is required'}), 400

        options_chain = instruments.list_nested_futures_option_chains(symbol, expiration_date)
        return jsonify({'options_chain': options_chain}), 200
    except Exception as e:
        return jsonify({'error': f"Error retrieving nested futures options chains: {e}"}), 500

if __name__ == "__main__":
    app.debug = True
    #Initialize necessary variables
    initialize_app()
    app.run()