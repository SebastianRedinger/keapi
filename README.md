# KeApi
[![Documentation Status](https://readthedocs.org/projects/keapi/badge/?version=latest)](https://keapi.readthedocs.io/en/latest/?badge=latest)
[![Publish 📦 to PyPI](https://github.com/SebastianRedinger/keapi/actions/workflows/python-publish-to-pypi.yml/badge.svg)](https://github.com/SebastianRedinger/keapi/actions/workflows/python-publish-to-pypi.yml)
[![PyPI version](https://img.shields.io/pypi/v/keapi-robotics)](https://pypi.org/project/keapi-robotics/)



KeApi is a Python package for communicating and
sending commands to your KEBA PLC via Web Sockets.

Note: This package is not affiliated with KEBA AG

## Who is this package for?
If you have a KEBA PLC and want to send commands to
it or monitor the state of it.

### Requirements
**RobotControl WebAPI 0.2.1-beta.1**  
**RobotControl API 0.2.1-beta.6**  
**Communication Utils Robotics 1.5.0** (Optional - For compatibility layer)

## Key Features
- Start and execute commands on the PLC
- Set and receive variables on the PLC
- Subscribe to cyclic and event based topics

## Documentation
The full documentation can be found at https://keapi.readthedocs.io

## Getting Started
### Installation
To install this package you can either use `python3 setup.py install` or `pip3 install keapi-robotics`

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

### Compatibility Layer
While **RobotControl WebAPI** is in beta some functions such as
`set_var` won't work. To counteract this, the Compatibility Layer
implements functions to get and set variables and to execute Teach Control
programs via TcWebApi.

#### Example
```
import keapi as ka
tc_var = ka.compat.connect_tc_var(192.168.1.1, Admin, pass)

# Get Var
pos_x = tc_var.get_var('TX2_90.RobotData.cartSetPos.x')

# Set Var
tc_var.set_var('IO.do_1', 1)
```
