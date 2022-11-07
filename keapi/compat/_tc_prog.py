from typing import Any
import requests
import json
import time
from keapi._error import HttpError, TcError


def connect_tc_prog(host: str, user: str, passwd: str, robot: str):
    """Establishes a connection to the TcApi and returns
    a instance of TcProg which can be used to start and
    stop programs that are already definen in Teach Control

    :param host: IP Address or Hostname of TcApi Server
    :type host: str
    :param user: Username to login to TcApi
    :type user: str
    :param passwd: Password to login to TcApi
    :type passwd: str
    :param robot: Name of the robot
    :type robot: str
    :return: TcProg instance
    :rtype: TcProg
    """
    tc = TcProg(robot)
    tc._connect(host, user, passwd)
    return tc


class TcProg:
    """Holds the Auth Cookie and the logic to communicate
    with the TcApi
    """
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
        """Starts a Teach Control programm and waits until
        it's execution is finished. This function is blocking

        :param project_name: Name of the Teach Control project
        :type project_name: str
        :param prog_name: Name of the Teach Control program
        :type prog_name: str
        :raises TcError: When another program is already active
        :raises HttpError: When http status code != 200
        """
        self.start(project_name, prog_name)
        # Not great
        while self.is_prog_running():
            time.sleep(0.1)
        self.stop()

    def start(self, project_name: str, prog_name: str):
        """Loads and starts a Teach Control program.

        :param project_name: Name of the Teach Control project
        :type project_name: str
        :param prog_name: Name of the Teach Control program
        :type prog_name: str
        :raises TcError: When another program is already active
        :raises HttpError: When http status code != 200
        """
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
        """Stops the currently executing program and unloads
        the Teach Control project.

        :raises TcError: When there is no program to stop
        :raises HttpError: When http status code != 200
        """
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
        """Loads a Teach Control Project

        :param project_name: Name of the project
        :type project_name: str
        :raises HttpError: When http status code != 200
        """
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
        """Unloads the currently loaded Teach Control
        project

        :raises TcError: When there is not project loaded
        :raises HttpError: When http status code != 200
        """
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
        """Returns whether a program is running or not

        :raises TcError: When there is no program started
        :raises HttpError: When http status code != 200
        :return: Program running
        :rtype: bool
        """
        if not self._prog_active:
            raise TcError('There is no program active.')
        url = f'http://{self._host}/api/v3/teach-control/programs/{self._robot}/{self._project_name}.tt/{self._program_name}.tip'
        res = requests.get(url, headers=self._http_headers,
                           cookies=self._cookie)
        if res.status_code != 200:
            raise HttpError(res.text)
        ans = json.loads(res.text)
        if 'executionTree' not in ans or ans['executionTree']['status']['state'] != 1:
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
