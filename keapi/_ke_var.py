from ._command_server import CommandServer
from typing import Any

param_lookup = {}


def set_variable(cmd_server: CommandServer, prefix: str, name: str, val: Any):
    """Sets a variable on the PLC

    :param cmd_server: CommandServer connection
    :type cmd_server: CommandServer
    :param prefix: Variable Prefix (e.g. APPL.Application.GVL)
    :type prefix: str
    :param name: Variable name
    :type name: str
    :param val: Variable value
    :type val: Any
    """
    if name not in param_lookup:
        get_variable(name)
    args = {}
    args['name'] = f'{prefix}.{name}'
    args['value'] = {param_lookup[name]: val}
    cmd_server.exec('set_variable', **args)


def create_variable_setter(cmd_server: CommandServer, prefix: str):
    """Creates a function to set variable values with
    a fixed `prefix` and `server`.

    Example:

    .. code-block:: python

        io = create_variable_setter(cmdserver, 'APPL.Application._IoMapping')
        io('do_0', True)

    :param cmd_server: CommandServer connection
    :type cmd_server: CommandServer
    :param prefix: Variable Prefix (e.g. APPL.Application.GVL)
    :type prefix: str
    :return: Function to set variable values
    """
    def inner(name: str, val: Any):
        set_variable(cmd_server, prefix, name, val)
    return inner


def get_variable(cmd_server: CommandServer, prefix: str, name: str) -> Any:
    """Returns the value of a given variable on the PLC

    :param cmd_server: CommandServer connection
    :type cmd_server: CommandServer
    :param prefix: Variable Prefix (e.g. APPL.Application.GVL)
    :type prefix: str
    :param name: Variable name
    :type name: str
    :return: Variable value
    :rtype: Any
    """
    global param_lookup
    var_name = f'{prefix}.{name}'
    ret = cmd_server.exec('get_variable', name=var_name)
    param_lookup[name] = list(ret.keys())[0]
    return list(ret.values())[0]


def create_variable_getter(cmd_server: CommandServer, prefix: str):
    """Creates a function to get variable values with
    a fixed `prefix` and `server`.

    Example:

    .. code-block:: python

        io = create_variable_getter(cmdserver, 'APPL.Application._IoMapping')
        val = io('do_0')

    :param cmd_server: CommandServer connection
    :type cmd_server: CommandServer
    :param prefix: Variable Prefix (e.g. APPL.Application.GVL)
    :type prefix: str
    :return: Function to get variable values
    """
    def inner(name: str):
        return get_variable(cmd_server, prefix, name)
    return inner
