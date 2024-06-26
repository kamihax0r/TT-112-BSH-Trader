from flask import Flask, jsonify
import connection_test
import positions
import balance
import customer_info
import session_manager

app = Flask(__name__)
app.config['CUSTOMER_INFO'] = {}
app.config['ACCOUNT_NUMBERS'] = []

def initialize_app():
    # Create a session
    session_manager.create_session()
    # Fetch customer info and account numbers
    customer_data = customer_info.get_customer_info()
    if 'error' not in customer_data:
        app.config['CUSTOMER_INFO'] = customer_data
        account_numbers = customer_info.get_acctNumbers()
        if 'error' not in account_numbers:
            app.config['ACCOUNT_NUMBERS'] = account_numbers
            print(f"Account Numbers: {account_numbers}")  # Debugging line
        else:
            print(f"Error retrieving account numbers: {account_numbers['error']}")
    else:
        print(f"Error retrieving customer info: {customer_data['error']}")

@app.route('/', methods=['GET'])
def home():
    return 'Welcome to the Tastytrade API Flask app!'

@app.route('/test-connection', methods=['GET'])
def test_connection_route():
    result = connection_test.test_connection()
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

@app.route('/positions', methods=['GET'])
def positions_route():
    current_positions = positions.get_current_positions()
    if 'error' in current_positions:
        return jsonify(current_positions), 400
    return jsonify({"positions": current_positions})

@app.route('/balances', methods=['GET'])
def balances_route():
    if not app.config['ACCOUNT_NUMBERS']:
        return jsonify({'error': 'No account numbers available'}), 400
    
    all_balances = balance.get_all_balances(app.config['ACCOUNT_NUMBERS'])
    return jsonify(all_balances)

if __name__ == '__main__':
    initialize_app()
    app.run(debug=True)
