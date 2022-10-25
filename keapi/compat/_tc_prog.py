from typing import Any
import requests
import json
import time
from keapi._error import HttpError, TcError


def connect_tc_prog(host: str, user: str, passwd: str, robot: str):
    tc = TcProg(robot)
    tc._connect(host, user, passwd)
    return tc


class TcProg:
    def __init__(self, robot: str) -> None:
        self._host = None
        self._cookie = None
        self._robot = robot
        self._project_name = None
        self._program_name = None
        self._http_headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self._prog_active = False

    def exec(self, project_name: str, prog_name: str):
        self.start(project_name, prog_name)
        # Not great
        while self.is_prog_running():
            time.sleep(0.1)
        self.stop()

    def start(self, project_name: str, prog_name: str):
        if self._prog_active:
            raise TcError('Another Program is already active.')
        self._project_name = project_name
        self._program_name = prog_name
        self._get_control_authority()
        # Load Project
        url = f'http://{self._host}/api/v3/teach-control/projects/{self._robot}/{self._project_name}.tt'
        body = json.dumps({'command': 'load'})
        res = requests.post(url, headers=self._http_headers,
                            data=body, cookies=self._cookie)
        if res.status_code != 200:
            raise HttpError(res.text)
        # Start Program
        url = f'http://{self._host}/api/v3/teach-control/programs/{self._robot}/{self._project_name}.tt/{self._program_name}.tip'
        body = json.dumps({'command': 'start'})
        res = requests.post(url, headers=self._http_headers,
                            data=body, cookies=self._cookie)
        if res.status_code != 200:
            raise HttpError(res.text)
        self._prog_active = True

    def stop(self):
        if not self._prog_active:
            raise TcError('There is no active program to stop.')
        # Stop Program
        url = f'http://{self._host}/api/v3/teach-control/programs/{self._robot}/{self._project_name}.tt/{self._program_name}.tip'
        body = json.dumps({'command': 'stop'})
        res = requests.post(url, headers=self._http_headers,
                            data=body, cookies=self._cookie)
        # Unload Project
        url = f'http://{self._host}/api/v3/teach-control/projects/{self._robot}/{self._project_name}.tt'
        body = json.dumps({'command': 'unload'})
        res = requests.post(url, headers=self._http_headers,
                            data=body, cookies=self._cookie)
        if res.status_code != 200:
            raise HttpError(res.text)
        self._release_control_authority()
        self._project_name = None
        self._program_name = None
        self._prog_active = False

    def load_project(self, project_name: str) -> None:
        self._get_control_authority()
        self._project_name = project_name
        url = f'http://{self._host}/api/v3/teach-control/projects/{self._robot}/{self._project_name}.tt'
        body = json.dumps({'command': 'load'})
        res = requests.post(url, headers=self._http_headers,
                            data=body, cookies=self._cookie)
        if res.status_code != 200:
            raise HttpError(res.text)
        self._release_control_authority()

    def unload_project(self) -> None:
        if not self._project_name:
            raise TcError('No Project loaded')
        self._get_control_authority()
        url = f'http://{self._host}/api/v3/teach-control/projects/{self._robot}/{self._project_name}.tt'
        body = json.dumps({'command': 'unload'})
        res = requests.post(url, headers=self._http_headers,
                            data=body, cookies=self._cookie)
        if res.status_code != 200:
            raise HttpError(res.text)
        self._project_name = None
        self._release_control_authority()

    def is_prog_running(self) -> bool:
        if not self._prog_active:
            raise TcError('There is no program active.')
        url = f'http://{self._host}/api/v3/teach-control/programs/{self._robot}/{self._project_name}.tt/{self._program_name}.tip'
        res = requests.get(url, headers=self._http_headers,
                           cookies=self._cookie)
        if res.status_code != 200:
            raise HttpError(res.text)
        ans = json.loads(res.text)
        if 'executionTree' not in ans or ans['executionTree']['status']['state'] != 3:
            return False
        return True

    def _connect(self, host: str, user: str, passwd: str) -> None:
        self._host = host
        url = f'http://{host}/access/login/'
        body = json.dumps({'username': user, 'password': passwd})
        res = json.loads(
            requests.post(url, headers=self._http_headers, data=body).text
            )
        self._cookie = {'accSvcId': str(res['session'])}
        self._release_control_authority()

    def _get_control_authority(self) -> None:
        url = f'http://{self._host}/api/v3/teach-control/rc/controlauthority/?robot={self._robot}'
        body = json.dumps({'deviceType': 'Bonder', 'simulate': False})
        res = requests.post(url, headers=self._http_headers,
                            data=body, cookies=self._cookie)
        if res.status_code != 200:
            raise HttpError(res.text)

    def _release_control_authority(self) -> None:
        url = f'http://{self._host}/api/v3/teach-control/rc/controlauthority/?robot={self._robot}&force=true'
        res = requests.delete(url, cookies=self._cookie)
        if res.status_code != 200:
            raise HttpError(res.text)
