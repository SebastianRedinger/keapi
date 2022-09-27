from _error import SocketError
import json
from threading import Thread, Lock
import websocket


def connect_to_socket(url):
    sub_server = SubscribeServer.instance()
    if sub_server.is_connected():
        raise SocketError('Already connected. Can not connect twice')
    sub_server.connect(url)


def disconnect_from_socket():
    sub_server = SubscribeServer.instance()
    if not sub_server.is_connected():
        raise SocketError('Already disconnected')
    sub_server.disconnect()


def subscribe_to_topic(topic: str, func=None, cycle_time=0.0):
    sub_server = SubscribeServer.instance()
    if not sub_server.is_connected():
        raise SocketError('No connection to server established')
    sub_server.subscribe(topic, func, cycle_time)


def unsubscribe_to_topic(topic: str, func=None):
    sub_server = SubscribeServer.instance()
    if not sub_server.is_connected():
        raise SocketError('No connection to server established')
    sub_server.unsubscribe(topic, func)


class SubscribeServer:
    _instance = None

    @staticmethod
    def instance():
        if SubscribeServer._instance is None:
            SubscribeServer()
        return SubscribeServer._instance

    def __init__(self) -> None:
        assert SubscribeServer._instance is None
        self._ws = None
        self._receiver_thread = None
        self._is_connected = False
        self._subscription_dict = {}
        self._lock = Lock()
        SubscribeServer._instance = self

    def connect(self, url):
        self._ws = websocket.WebSocketApp(url,
                                          subprotocols=['RcWebApi.v1.json'],
                                          on_message=self._message_handler,
                                          on_error=self._error_handler,
                                          on_open=self._open_handler)
        self._receiver_thread = Thread(target=self._thread_fun)
        self._receiver_thread.start()

    def disconnect(self):
        with self._lock:
            self._subscription_dict = {}
        self._is_connected = False
        self._ws.close()
        self._receiver_thread.join(5)
        self._receiver_thread = None
        self._ws = None

    def is_connected(self) -> bool:
        return self._is_connected

    def subscribe(self, topic: str, func=None, cycle_time=0.0):
        assert func is not None
        with self._lock:
            if topic in self._subscription_dict:
                self._subscription_dict[topic].append(func)
            else:
                self._subscription_dict[topic] = [func]
                req = {}
                req['request'] = 0
                req['subscribe'] = topic
                if cycle_time > 0.0:
                    req['args'] = {'cycle_time_s': cycle_time}
        if req:
            self._ws.send(json.dumps(req))

    def unsubscribe(self, topic: str, func=None):
        def _unsub_req(self, topic):
            req = {}
            req['request'] = 0
            req['unsubscribe'] = topic
            self._ws.send(json.dumps(req))
        with self._lock:
            if func is None or len(self._subscription_dict[topic]) == 1:
                del self._subscription_dict[topic]
                _unsub_req(self, topic)
            else:
                self._subscription_dict[topic].remove(func)

    def _message_handler(self, ws, message):
        json_msg = json.loads(message)
        if 'topic' in json_msg:
            topic = json_msg['topic']
            with self._lock:
                for func in self._subscription_dict[topic]:
                    func(json_msg)

    def _error_handler(self, ws, error):
        raise SocketError(error)

    def _open_handler(self, ws):
        self._is_connected = True

    def _thread_fun(self):
        self._ws.run_forever()


if __name__ == '__main__':
    URL = "ws://192.168.71.3:20004/TX2_90/websocket-subscribe"
    from cprint import cprint

    def t1(message):
        print('Topic1')
        print(message)

    def t2(message):
        print('Topic2')
        print(message)

    connect_to_socket(URL)
    while True:
        try:
            print(eval(input('>>>')))
        except KeyboardInterrupt:
            cprint.ok('ENDE')
            disconnect_from_socket()
            break
        except Exception as ex:
            cprint.fatal(ex, interrupt=False)
