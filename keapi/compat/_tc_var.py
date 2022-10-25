from typing import Any
import requests
import json
from keapi._error import HttpError


def connect_tc_var(host: str, user: str, passwd: str):
    """Establishes a connection to the TcApi and returns
    a instance of TcVar which can be used to set and get
    variables via Teach Control

    :param host: IP Address or Hostname of TcApi Server
    :type host: str
    :param user: Username to login to TcApi
    :type user: str
    :param passwd: Password to login to TcApi
    :type passwd: str
    :return: TcVar instance
    :rtype: TcVar
    """
    tc = TcVar()
    tc._connect(host, user, passwd)
    return tc


class TcVar:
    """Holds the Auth Cookie and the logic to communicate
    with the TcApi
    """
    def __init__(self) -> None:
        self._host = None
        self._cookie = None
        self._http_headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def set_var(self, path: str, val: Any):
        """Sets a Variable on the PLC via the TcApi

        :param path: Full path to the Variable '.' seperated
        :type path: str
        :param val: Value to be set
        :type val: Any
        :raises HttpError: When set was unsuccessful
        """
        url = f'http://{self._host}/api/v3/teach-control/variables/{path}'
        body = json.dumps({'value': val})
        res = requests.post(
            url, headers=self._http_headers, data=body, cookies=self._cookie
            )
        if res.status_code != 200:
            info = json.loads(res.text)['info']
            raise HttpError(info)

    def get_var(self, path: str) -> Any:
        """Gets a Variable from the PLC via the TcApi

        :param path: Full path to the Variable '.' seperated
        :type path: str
        :raises HttpError: When get was unsuccessful
        :return: Variable value
        :rtype: Any
        """
        url = f'http://{self._host}/api/v3/teach-control/variables/{path}'
        res = requests.get(
            url, headers=self._http_headers, cookies=self._cookie
            )
        if res.status_code != 200:
            info = json.loads(res.text)['info']
            raise HttpError(info)
        return json.loads(res.text)['varInfos']['value']

    def _connect(self, host: str, user: str, passwd: str) -> None:
        self._host = host
        url = f'http://{host}/access/login/'
        body = json.dumps({'username': user, 'password': passwd})
        res = json.loads(
            requests.post(url, headers=self._http_headers, data=body).text
            )
        self._cookie = {'accSvcId': str(res['session'])}
