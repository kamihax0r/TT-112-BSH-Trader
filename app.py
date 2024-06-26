from flask import Flask, jsonify
from session_manager import SessionManager
from customer_info import CustomerInfo
from orders import Orders
from positions import Positions

app = Flask(__name__)

session_manager = SessionManager()
orders_info = None
customer_info = None
positions_info = None

def initialize_app():
    global orders_info, customer_info
    try:
        session_manager.create_session()
        headers = session_manager.get_headers()
        #print(f"Headers in initialize_app: {headers}")

        # Initialize the customer info
        customer_info = CustomerInfo(headers)
        # Initialize orders
        orders_info = Orders(session_manager)
        # Initialize positions
        positions_info = Positions(session_manager)
        
        # Fetch positions for all accounts and store them
        account_numbers = customer_info.get_acct_numbers()
        all_positions = {}
        for account_number in account_numbers:
            all_positions[account_number] = positions_info.list_positions(account_number)

        app.config['POSITIONS'] = all_positions
        
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
    positions = app.config.get('POSITIONS', {})
    if not positions:
        return jsonify({'error': 'No positions found'}), 500
    return jsonify({'positions': positions})    

if __name__ == '__main__':
    initialize_app()
    app.run(debug=True)
