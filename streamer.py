import websocket
import json
from constants import STREAMER_URL

class Streamer:
    def __init__(self, session_manager, account_numbers):
        self.session_manager = session_manager
        self.account_numbers = account_numbers
        self.ws = None

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            print(f"Received message: {data}")

            # Handle different types of messages
            if 'type' in data and data['type'] == 'Greeks':
                self.handle_greeks_data(data['data'])
        except Exception as e:
            print(f"Error processing message: {e}")

    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")

    def on_open(self, ws):
        print("WebSocket connection opened")
        self.subscribe_to_account_updates()

    def start(self):
        self.ws = websocket.WebSocketApp(
            STREAMER_URL,
            header=self.session_manager.get_headers(),
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        self.ws.run_forever()

    def subscribe_to_account_updates(self):
        subscribe_message = {
            "action": "connect",
            "value": self.account_numbers,
            "auth-token": self.session_manager.get_session_token()
        }
        self.ws.send(json.dumps(subscribe_message))
        print(f"Subscribed to account updates for: {self.account_numbers}")

    def handle_greeks_data(self, data):
        # Implement logic to handle Greeks data
        print(f"Greeks data: {data}")
