from flask import Flask, jsonify, request
from session_manager import SessionManager
from customer_info import CustomerInfo
from orders import Orders
from streamer import Streamer
from account import Account
from instruments import Instruments

app = Flask(__name__)

session_manager = SessionManager()
orders_info = None
customer_info = None
account_positions = {}
account_balances = {}
accounts = []  # Initialize the global accounts list
streamer = None
instruments = None

def initialize_app():
    global orders_info, customer_info, account_positions, account_balances, accounts, streamer, instruments
    try:
        session_manager.create_session()
        headers = session_manager.get_headers()
        print(f"Headers in initialize_app: {headers}")

        # Initialize the customer info
        customer_info = CustomerInfo(headers)
        # Initialize orders
        orders_info = Orders(session_manager)

        # Fetch account numbers
        account_numbers = customer_info.get_acct_numbers()

        # Fetch positions and balances for all accounts and store them
        for account_number in account_numbers:
            account = Account(account_number, session_manager)
            positions = account.get_positions()
            balance = account.get_balance()
            account_positions[account_number] = positions
            account_balances[account_number] = balance
            accounts.append(account)

        # Initialize and start the streamer
        streamer = Streamer(session_manager, account_numbers)
        streamer.start()
        
        # Initialize an instance of instruments to call functions when needed
        instruments = Instruments(session_manager)

    except Exception as e:
        print(f"Error during initialization: {e}")

@app.route('/', methods=['GET'])
def home():
    return 'Welcome to the Tastytrade API Flask app!'

@app.route('/test-connection', methods=['GET'])
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
    global account_positions
    if not account_positions:
        return jsonify({'error': 'No positions found'}), 500
    return jsonify({'positions': account_positions})

@app.route('/balances', methods=['GET'])
def balances_route():
    global account_balances
    if not account_balances:
        return jsonify({'error': 'No balances found'}), 500
    return jsonify({'balances': account_balances})

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
def all_account_greeks_route():
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
    
# Order-related endpoints
@app.route('/orders/<account_number>', methods=['GET'])
def get_orders_route(account_number):
    global orders_info
    start_date = request.args.get('start-date')
    end_date = request.args.get('end-date')
    underlying_symbol = request.args.get('underlying-symbol')
    status = request.args.get('status')
    sort = request.args.get('sort', 'Desc')
    per_page = request.args.get('per-page', 10)
    page_offset = request.args.get('page-offset', 0)

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
    
if __name__ == '__main__':
    initialize_app()
    app.run(debug=True)
