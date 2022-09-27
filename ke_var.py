from command_server import CommandServer
param_lookup = {}


def set_variable(name, val):
    if name not in param_lookup:
        get_variable(name)
    args = {}
    args['name'] = name
    args['value'] = {param_lookup[name]: val}
    CommandServer.instance.exec_sync('set_variable', **args)


def get_variable(name):
    global param_lookup
    ret = CommandServer.instance.exec_sync('get_variable', name=name)
    param_lookup[name] = list(ret.keys())[0]
    return list(ret.values())[0]


class KeVar:
    def __init__(self, domain) -> None:
        super().__setattr__('domain', domain)

    def __setattr__(self, name: str, value) -> None:
        set_variable(f'{self.domain}.{name}', value)

    def __getattr__(self, name: str):
        return get_variable(f'{self.domain}.{name}')


if __name__ == '__main__':
    COMMAND_CONNECTION_URL = "ws://192.168.71.3:20004/TX2_90/websocket-command"
    srv = CommandServer().instance
    try:
        srv.connect(COMMAND_CONNECTION_URL)

        ret = get_variable('APPL.Application._IoMapping.do_0')
        print(ret)

        iomapping = KeVar('APPL.Application._IoMapping')
        iomapping.do_0 = True
        print(iomapping.do_0)

        print('ENDE')
    finally:
        srv.disconnect()
