from ._error import SocketError
import json
import websocket
from threading import Thread, Lock


def connect_subscriber(url: str):
    """Establishes a connection to the RcWebApi Subscribe
    Socket and returns SubscribeServer object which can
    be used to interact with the socket.

    :param url: Full URL to socket
        (e.g. ws://IP:PORT/Robot/websocket-subscribe)
    :type url: str
    :return: SubscribeServer object
    :rtype: SubscribeServer
    """
    srv = SubscribeServer()
    srv._connect(url)
    return srv


class SubscribeServer:
    """Holds the connection to the RcWebApi's subscribe
    socket. Provides a low level API to subscribe and
    unsubscribe to topics predefined by KEBA.

    :raises SocketError: When there is a problem while
        receiving the answer from the socket
    """
    def __init__(self) -> None:
        self._ws = None
        self._receiver_thread = None
        self._is_connected = False
        self._subscription_dict = {}
        self._lock = Lock()

    def disconnect(self):
        """Unsubscribes from all active subscriptions
        and closes the connection to the socket.
        """
        with self._lock:
            self._subscription_dict = {}
        self._is_connected = False
        self._ws.close()
        self._receiver_thread.join(5)
        self._receiver_thread = None
        self._ws = None

    def is_connected(self) -> bool:
        """Returns whether the socket ist connected
        or not.

        :return: Is connection open
        :rtype: bool
        """
        return self._is_connected

    def subscribe(self, topic: str, func=None, cycle_time=0.0):
        """Subscribes to a topic. The topic can be a cyclic or
        event based type.
        The passed function is called when the topic sends an answer.
        Leave the cycle_time to 0.0 if subscribing to an event based
        topic.
        A topic can be subscribed to multiple times with different
        functions. If it is a cyclic topic the cycle_time from
        the first call will be used.

        :param topic: RcWebApi Topic Name
        :type topic: str
        :param func: Function that will be called when topic returns
            an answer.
        :type func: function
        :param cycle_time: Time in seconds how often a topic should
            return an answer, defaults to 0.0. If left to 0.0 it is assumed
            that an event based topic is subscribed
        :type cycle_time: float, optional
        """
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
        """Unsubscribe from a previously subscribed topic.
        Can be used to unsubscribe all functions from a topic
        by leaving `func=None`. If only a specific function
        should be unsubscribed pass the function in parameter
        `func`.

        :param topic: RcWebApi Topic Name
        :type topic: str
        :param func: Function that should be unsubscribed,
            defaults to None
        :type func: function, optional
        """
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

    def _connect(self, url):
        self._ws = websocket.WebSocketApp(url,
                                          subprotocols=['RcWebApi.v1.json'],
                                          on_message=self._message_handler,
                                          on_error=self._error_handler,
                                          on_open=self._open_handler)
        self._receiver_thread = Thread(target=self._thread_fun)
        self._receiver_thread.start()

    def _message_handler(self, ws, message):
        json_msg = json.loads(message)
        if 'topic' in json_msg:
            topic = json_msg['topic']
            if topic not in self._subscription_dict:
                return
            with self._lock:
                for func in self._subscription_dict[topic]:
                    func(json_msg)

    def _error_handler(self, ws, error):
        raise SocketError(error)

    def _open_handler(self, ws):
        self._is_connected = True

    def _thread_fun(self):
        self._ws.run_forever()
