import websocket
import json
import threading

class Streamer:
    def __init__(self, session_token, account_numbers):
        self.session_token = session_token
        self.account_numbers = account_numbers
        self.ws = None
        self.listeners = []

    def on_message(self, ws, message):
        data = json.loads(message)
        for listener in self.listeners:
            listener(data)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(self, ws):
        def run(*args):
            self.send_heartbeat()
            self.subscribe_to_account_updates()

        threading.Thread(target=run).start()

    def send_heartbeat(self):
        heartbeat_message = json.dumps({
            "action": "heartbeat",
            "auth-token": self.session_token,
            "request-id": 1
        })
        self.ws.send(heartbeat_message)

    def subscribe_to_account_updates(self):
        connect_message = json.dumps({
            "action": "connect",
            "value": self.account_numbers,
            "auth-token": self.session_token,
            "request-id": 2
        })
        self.ws.send(connect_message)

    def add_listener(self, listener):
        self.listeners.append(listener)

    def start(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://streamer.cert.tastyworks.com",
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()

def initialize_streamer(session_token, account_numbers):
    streamer = Streamer(session_token, account_numbers)
    streamer_thread = threading.Thread(target=streamer.start)
    streamer_thread.start()
    return streamer
