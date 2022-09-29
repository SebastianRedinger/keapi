from ._error import KebaError, HttpError
import json
import websocket
from enum import Enum
from typing import Any
from threading import Thread, Lock, Condition


class Ticket:
    """A Ticket represents one command sent to the socket.
    While the ticket is in state `BUSY` it has not yet been
    completed. If a ticket completes with an error the
    corresponding exception is raised. If a ticket completes
    normaly the result is returned.

    :raises TimeoutError: When wait timeout is reached
    :raises HttpError: When the request has an error on the
        users side (e.g. wrong usage of command)
    :raises KebaError: When the error is on the PLC
    """

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
            return f'State: {self._state} RequestId: {self._request_id}'

    def wait(self, timeout=None) -> Any:
        """Waits and blocks until the ticket is completed or
        the timeout is reached.

        :param timeout: Timeout in seconds. If left to `None`
            it waits forever. Defaults to None
        :type timeout: float, optional
        :return: Result of the sent command. can be none if
            there is no result for the command
        :rtype: Any
        """
        def predicate(state) -> bool:
            return state != self.State.BUSY

        with self.server._lock:
            self.server._condition.wait_for(
                lambda: predicate(self._state), timeout
                )

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
                    return None

    def requestid(self) -> int:
        """Unique request id for this ticket. This is used
        to associate a ticket to a command.

        :return: request id
        :rtype: int
        """
        return self._request_id

    @property
    def state(self) -> State:
        """Current state of the Ticket

        :return: State
        :rtype: State
        """
        with self.server._lock:
            return self._state

    def _route_mux_locked(self, answer) -> bool:
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


def connect_commands(url: str):
    """Establishes a connection to the RcWebApi Commands
    Socket and returns CommandServer object which can
    be used to interact with the socket.

    :param url: Full URL to socket
        (e.g. ws://IP:PORT/Robot/websocket-command)
    :type url: str
    :return: CommandServer object
    :rtype: CommandServer
    """
    srv = CommandServer()
    srv._connect(url)
    return srv


class CommandServer:
    """Holds the connection to the RcWebApi's command
    socket. Provides a low level API to execute or start
    commands on the KEBA PLC

    :raises HttpError: When the connection to the socket
        was unsuccessful.
    """
    def __init__(self) -> None:
        self._ws = None
        self._receiver_thread = None
        self._receiver_thread_stop = False
        self._rec_id_counter = 0
        self._ticket_list = []
        self._lock = Lock()
        self._condition = Condition(self._lock)

    def disconnect(self):
        """Disconnects from the socket.
        """
        self._receiver_thread_stop = True
        self._ws.close()
        self._receiver_thread.join(5)
        self._receiver_thread = None
        self._ws = None

    def is_connected(self) -> bool:
        """Returns whether the socket is connected
        or not.

        :return: Is connection open
        :rtype: bool
        """
        if self._ws:
            return self._ws.connected
        else:
            return False

    def start(self, cmd: str, **kwargs) -> Ticket:
        """Sends the given command and it's parameters
        to the PLC returns a ticket

        :param cmd: PLC command
        :type cmd: str
        :return: Ticket of given command
        :rtype: Ticket
        """
        with self._lock:
            self._rec_id_counter += 1
            t = Ticket(self, self._rec_id_counter)
            self._ticket_list.append(t)
            data = {}
            data['request'] = self._rec_id_counter
            data['cmd'] = cmd
            if len(kwargs) > 0:
                data['args'] = kwargs
        self._ws.send(json.dumps(data))
        return t

    def exec(self, cmd: str, **kwargs) -> Any:
        """Sends the given command and it's parameters
        to the PLC and waits till it's finished. This
        method is blocking. Returns the result of the
        executed command.

        :param cmd: PLC command
        :type cmd: str
        :return: Command result
        :rtype: Any
        """
        t = self.start(cmd, **kwargs)
        return t.wait()

    def _connect(self, url):
        self._rec_id_counter = 0
        self._ws = websocket.WebSocket()
        self._ws.connect(url, subprotocols=['RcWebApi.v1.json'])
        ret = json.loads(self._ws.recv())
        if ret['status'] != 200:
            raise HttpError(
                'Connection to Keba Socket could not be esablished.'
                )
        self._receiver_thread_stop = False
        self._receiver_thread = Thread(target=self._thread_fun)
        self._receiver_thread.start()

    def _thread_fun(self):
        while not self._receiver_thread_stop:
            ret = self._ws.recv()
            with self._lock:
                for t in self._ticket_list:
                    if t._route_mux_locked(ret):
                        self._ticket_list.remove(t)
                        break
                self._condition.notify_all()
