from flask import Flask, jsonify
import connection_test
import customer_info
import positions
import orders
import streamer

app = Flask(__name__)
app.config['CUSTOMER_INFO'] = {}
app.config['ACCOUNT_NUMBERS'] = []
app.config['POSITIONS'] = {}
app.config['MARGIN_REQUIREMENTS'] = {}
app.config['STREAMER'] = None

def initialize_app():
    customer_data = customer_info.get_customer_info()
    if 'error' not in customer_data:
        app.config['CUSTOMER_INFO'] = customer_data
        account_numbers = customer_info.get_acct_numbers()
        if 'error' not in account_numbers:
            app.config['ACCOUNT_NUMBERS'] = account_numbers

            # Fetch and store positions for all accounts
            positions_data = {}
            for account_number in account_numbers:
                positions_data[account_number] = positions.Positions().list_positions(account_number)
            app.config['POSITIONS'] = positions_data

            # Fetch and store margin requirements for all accounts
            margin_requirements_data = {}
            for account_number in account_numbers:
                margin_requirements_data[account_number] = positions.Positions().get_account_margin_requirements(account_number)
            app.config['MARGIN_REQUIREMENTS'] = margin_requirements_data

            # Initialize the streamer
            session_token = customer_info.get_session_token()
            app.config['STREAMER'] = streamer.initialize_streamer(session_token, account_numbers)
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
    current_positions = app.config['POSITIONS']
    if not current_positions:
        return jsonify({'error': 'No positions found'}), 400
    return jsonify({"positions": current_positions})

@app.route('/balances', methods=['GET'])
def balances_route():
    if not app.config['ACCOUNT_NUMBERS']:
        return jsonify({'error': 'No account numbers available'}), 400

    all_balances = positions.Positions().get_all_balances(app.config['ACCOUNT_NUMBERS'])
    return jsonify(all_balances)

@app.route('/margin-requirements', methods=['GET'])
def margin_requirements_route():
    margin_requirements = app.config['MARGIN_REQUIREMENTS']
    if not margin_requirements:
        return jsonify({'error': 'No margin requirements found'}), 400
    return jsonify(margin_requirements)

if __name__ == '__main__':
    initialize_app()
    app.run(debug=True)
