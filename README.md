# KeApi
[![Documentation Status](https://readthedocs.org/projects/keapi/badge/?version=latest)](https://keapi.readthedocs.io/en/latest/?badge=latest)
[![Publish 📦 to PyPI](https://github.com/SebastianRedinger/keapi/actions/workflows/python-publish-to-pypi.yml/badge.svg?branch=1.0)](https://github.com/SebastianRedinger/keapi/actions/workflows/python-publish-to-pypi.yml)
[![Publish 📦 to TestPyPI](https://github.com/SebastianRedinger/keapi/actions/workflows/python-publish-to-test-pypi.yml/badge.svg?branch=1.0)](https://github.com/SebastianRedinger/keapi/actions/workflows/python-publish-to-test-pypi.yml)


KeApi is a Python package for communicating and
sending commands to your KEBA PLC via Web Sockets.

Note: This package is not affiliated with KEBA AG

## Who is this package for?
If you have a KEBA PLC and want to send commands to
it or monitor the state of it.

### Requirements
**RobotControl WebAPI 0.2.1-beta.1**  
**RobotControl API 0.2.1-beta.6**  
**Communication Utils Robotics 1.5.0** (Optional)  

## Key Features
- Start and execute commands on the PLC
- Set and receive variables on the PLC
- Subscribe to cyclic and event based topics

## Getting Started
### Installation
To install this package you can either use `python3 setup.py install` or `pip3 install keapi`

### Usage
To get startet you first need to connect to the applicalbe web sockets.

```
import keapi as ka
cmdserver = ka.connect_commands('ws://IP:PORT/ROBOT/websocket-command')
subserver = ka.connect_subscriber('ws://IP:PORT/ROBOT/websocket-subscribe')
```

Once connected you are all set to send commands or subscribe to events.

#### Example
```
cmdserver.exec('set_active_client')

pos = {
    'joints': {
        'main_joints': [0, 0, 120, 0, 0, 0]
    }
}
ticket = cmdserver.start('path_ptp', position=pos)
ticket.wait()
```

The full documentation can be found at https://keapi.readthedocs.io
