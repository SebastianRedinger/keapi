import json
from threading import Thread
import websocket


class SubscrubeServer:
    def __init__(self) -> None:
        self._ws = None
        self._receiver_thread = None

    def connect(self, url, on_open=None, on_message=None, on_error=None, on_close=None):
        self._ws = websocket.WebSocket()
        self._ws = websocket.WebSocketApp(url,
                                          subprotocols=['RcWebApi.v1.json'],
                                          on_open=on_open,
                                          on_message=on_message,
                                          on_error=on_error,
                                          on_close=on_close)
        self._receiver_thread = Thread(target=self._thread_fun)
        self._receiver_thread.start()

    def disconnect(self):
        self._ws.close()
        self._receiver_thread.join(5)
        self._receiver_thread = None
        self._ws = None

    def subscribe(self, topic: str, cycle_time=0.0):
        req = {}
        req['request'] = 0
        req['subscribe'] = topic
        if cycle_time > 0.0:
            req['args'] = {'cycle_time_s': cycle_time}
        self._ws.send(json.dumps(req))

    def unsubscribe(self, topic: str):
        req = {}
        req['request'] = 0
        req['unsubscribe'] = topic
        self._ws.send(json.dumps(req))

    def _thread_fun(self):
        self._ws.run_forever()


if __name__ == '__main__':
    import globvars
    from cprint import cprint

    def on_message(ws, message):
        print(message)

    def on_error(ws, error):
        print(error)

    def on_close(ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(ws):
        print("Opened connection")

    sub = SubscrubeServer()
    sub.connect(globvars.SUBSCRIBE_CONNECTION_URL, on_message=on_message, on_close=on_close, on_open=on_open)
    while True:
        try:
            print(eval(input('>>>')))
        except KeyboardInterrupt:
            cprint.ok('ENDE')
            sub.disconnect()
            break
        except Exception as ex:
            cprint.fatal(ex, interrupt=False)
