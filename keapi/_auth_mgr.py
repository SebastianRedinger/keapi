import requests
import json
from ._error import HttpError


class AuthMgr:
    """Holds the auth_token, client_id, PCL IP
    and robot name

    :raises HttpError: When the authorisation was
    unsuccessful
    """
    def __init__(self) -> None:
        self._host_ip = None
        self._robot_name = None
        self._auth_token = None
        self._client_id = None

        self._http_headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def login(self, ip: str, robot_name: str, user: str, passwd: str) -> None:
        self._host_ip = ip
        self._robot_name = robot_name
        url = f'http://{ip}/access/login/'
        body = json.dumps({'username': user, 'password': passwd})
        res = json.loads(
            requests.post(url, headers=self._http_headers, data=body).text
            )
        if res['status'] != "OK":
            raise HttpError(str(res['info']))
        self._auth_token = str(res['token'])

    def auth_token(self) -> str:
        if not self._auth_token:
            raise HttpError("Not logged in yet")
        return self._auth_token

    def host_ip(self) -> str:
        if not self._host_ip:
            raise HttpError("Not logged in yet")
        return self._host_ip

    def robot_name(self) -> str:
        if not self._robot_name:
            raise HttpError("Not logged in yet")
        return self._robot_name

    def client_id(self) -> int:
        if not self._client_id:
            raise HttpError("No client id set")
        return self._client_id

    def set_client_id(self, id: int) -> None:
        self._client_id = id

    def is_client_id_set(self) -> bool:
        return self._client_id is not None
