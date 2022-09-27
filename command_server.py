import json
from threading import Thread, Lock, Condition
import websocket
from enum import Enum
from _error import KebaError, HttpError, SocketError


class Ticket:
    '''
    Ein Ticket bildet einen Request an die Keba Steuerung ab.
    Das Ticket hat einen Status und kann Exceptions werfen.
    '''

    class State(Enum):
        BUSY = 1,
        DONE = 2,
        HTTP_ERROR = 3,
        KEBA_ERROR = 4

    def __init__(self, server, id) -> None:
        self.server = server
        self._request_id = id
        self._state = self.State.BUSY
        self._response = None

    def __str__(self) -> str:
        with self.server._lock:
            return f'Stauts: {self._state} RequestId: {self._request_id}'

    def wait(self, timeout=None):
        '''
        Wartet mit timeout auf response und wirft Exception
        wenn es schlecht lauft
        '''
        def predicate(state) -> bool:
            return state != self.State.BUSY

        with self.server._lock:
            self.server._condition.wait_for(lambda: predicate(self._state), timeout)

            if self._state == self.State.BUSY:
                raise TimeoutError('Ticket.Wait - Timeout reached')

            if self._state == self.State.HTTP_ERROR:
                err = self._response['error']
                raise HttpError(f'Request Error: {err}')
            elif self._state == self.State.KEBA_ERROR:
                err = self._response['error']
                raise KebaError(f'Keba Error: {err}')
            else:
                if 'result' in self._response:
                    return self._response['result']
                else:
                    return 'DONE... Schau ma mal'

    def requestid(self) -> int:
        '''Mutex muss nicht genommen werden weil const'''
        return self._request_id

    @property
    def state(self) -> State:
        with self.server._lock:
            return self._state

    def _route_mux_locked(self, answer) -> bool:
        '''
        Interne Funktion!
        Prueft ob response code mit dem vom Ticket uebereinstimmt
        Mutex ist zum Zeitpunkt des aufrufs gelocked
        '''
        j_ans = json.loads(answer)
        if j_ans['response'] == self._request_id:
            if j_ans['status'] == 200:
                self._state = self.State.DONE
            elif j_ans['status'] == 400:
                self._state = self.State.HTTP_ERROR
            elif j_ans['status'] == 900:
                self._state = self.State.KEBA_ERROR
            self._response = j_ans
            return True
        else:
            return False


def connect_to_socket(url):
    com_server = CommandServer.instance()
    if com_server.is_connected():
        raise SocketError('Already connected. Can not connect twice')
    com_server.connect(url)


def disconnect_from_socket():
    com_server = CommandServer.instance()
    if not com_server.is_connected():
        raise SocketError('Already disconnected')
    com_server.disconnect()


def start(cmd: str, **kwargs) -> Ticket:
    com_server = CommandServer.instance()
    if not com_server.is_connected():
        raise SocketError('No connection to server established')
    com_server.start(str, **kwargs)


def exec(self, cmd: str, **kwargs) -> str:
    com_server = CommandServer.instance()
    if not com_server.is_connected():
        raise SocketError('No connection to server established')
    com_server.exec(cmd, **kwargs)


class CommandServer:
    '''
    Zentrale Stelle, um Keba RcWebApi Kommandos zu managed
    '''
    _instance = None

    @staticmethod
    def instance():
        if vars._instance is None:
            CommandServer()
        return CommandServer._instance

    def __init__(self) -> None:
        assert CommandServer._instance is None
        self._ws = None
        self._receiver_thread = None
        self._receiver_thread_stop = False
        self._rec_id_counter = 0
        self._ticket_list = []
        self._lock = Lock()
        self._condition = Condition(self._lock)
        CommandServer._instance = self

    def connect(self, url):
        self._rec_id_counter = 0
        self._ws = websocket.WebSocket()
        self._ws.connect(url, subprotocols=['RcWebApi.v1.json'])
        ret = json.loads(self._ws.recv())
        if ret['status'] != 200:
            raise HttpError('Connection to Keba Socket could not be esablished.')
        self._receiver_thread_stop = False
        self._receiver_thread = Thread(target=self._thread_fun)
        self._receiver_thread.start()

    def disconnect(self):
        self._receiver_thread_stop = True
        self._ws.close()
        self._receiver_thread.join(5)
        self._receiver_thread = None
        self._ws = None

    def is_connected(self) -> bool:
        return self._ws.connected

    def start(self, cmd: str, **kwargs) -> Ticket:
        with self._lock:
            self._rec_id_counter += 1
            t = Ticket(self, self._rec_id_counter)
            self._ticket_list.append(t)
            # Request zusammen stoppeln
            data = {}
            data['request'] = self._rec_id_counter
            data['cmd'] = cmd
            if len(kwargs) > 0:
                data['args'] = kwargs
        # Absichtlich ausserhalb der Mutex senden
        self._ws.send(json.dumps(data))
        return t

    def exec(self, cmd: str, **kwargs) -> str:
        t = self.start(cmd, **kwargs)
        return t.wait()

    def _thread_fun(self):
        while not self._receiver_thread_stop:
            ret = self._ws.recv()
            with self._lock:
                for t in self._ticket_list:
                    if t._route_mux_locked(ret):
                        self._ticket_list.remove(t)
                        break
                self._condition.notify_all()


if __name__ == '__main__':
    COMMAND_CONNECTION_URL = "ws://192.168.71.3:20004/TX2_90/websocket-command"
    from cprint import cprint
    cmd = CommandServer()
    cmd.connect(COMMAND_CONNECTION_URL)
    while True:
        try:
            print(eval(input('>>>')))
        except KeyboardInterrupt:
            cprint.ok('ENDE')
            cmd.disconnect()
            break
        except Exception as ex:
            cprint.fatal(ex, interrupt=False)
