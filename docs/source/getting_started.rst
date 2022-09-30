###############
Getting Started
###############

Connecting
----------

To get startet you first need to connect to the applicalbe web sockets.
This API currently provides functionality to connect to the *command* and
*subscribe* web socket respectively.

.. code-block:: python

    import keapi as ka
    cmdserver = ka.connect_commands('ws://IP:PORT/ROBOT/websocket-command')
    subserver = ka.connect_subscriber('ws://IP:PORT/ROBOT/websocket-subscribe')


Commands
--------

After connecting you are all set to send your first command. To see a full
list of available commands please consult the API reference provided by KEBA.

There are two ways to send a command:
 - `exec`: Sends a command and waits for it's result
 - `start`: Sends a command and returns a `Ticket`

.. code-block:: python

    cmdserver.exec('set_active_client')

    pos = {
        'joints': {
            'main_joints': [0, 0, 120, 0, 0, 0]
        }
    }
    ticket = cmdserver.start('path_ptp', position=pos)
    ticket.wait()

Variables
---------
**Note: This feature is not yet supported in RobotControl WebAPI 0.2.1-beta.1**

To get and set variables on the PLC you need the full path of the variable and
an active connection to the *command* web socket.

.. code-block:: python

    var = ka.get_variable(cmdserver, 'APPL.Application._IoMapping', 'do_0')
    ka.set_variable(cmdserver, 'APPL.Application._IoMapping', 'do_0', True)

You can also create a variable group. This is a convenience function so you
don't have to write the full variable path every time.

.. code-block:: python

    getio = ka.create_variable_getter(cmdserver, 'APPL.Application._IoMapping')
    do = getio('do_0')

    setio = ka.create_variable_setter(cmdserver, 'APPL.Application._IoMapping')
    setio('do_0', True)

Subscription
------------

To subscribe to a topic you need to have a callback function which will
be called once the subscribed topic returns an answer.

.. code-block:: python

    def callback(msg):
        print(msg)

    def some_other_func():
        subserver.subscribe('robot_status', callback, 0.1)
        # Do stuff
        subserver.unsubscribe('robot_status', callback)

