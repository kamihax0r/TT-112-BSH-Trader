from flask import Flask, jsonify
from session_manager import SessionManager
from customer_info import CustomerInfo
from orders import Orders
from account import Account

app = Flask(__name__)

session_manager = SessionManager()
orders_info = None
customer_info = None
account_positions = {}
account_balances = {}

def initialize_app():
    global orders_info, customer_info, account_positions, account_balances
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
            account = Account(account_number)
            positions = account.get_positions()
            balance = account.get_balance()
            account_positions[account_number] = positions
            account_balances[account_number] = balance

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

if __name__ == '__main__':
    initialize_app()
    app.run(debug=True)
