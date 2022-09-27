from command_server import CommandServer, Ticket


class KeCommand:
    def __init__(self, name) -> None:
        self.name = name
        self.arguments = None

    @property
    def args(self):
        return self.arguments

    @args.setter
    def args(self, args: dict):
        self.arguments = args

    def go(self) -> Ticket:
        if self.arguments:
            return CommandServer.instance.exec_async(self.name, **self.arguments)
        else:
            return CommandServer.instance.exec_async(self.name)


if __name__ == '__main__':
    import globvars
    srv = CommandServer().instance
    try:
        srv.connect(globvars.COMMAND_CONNECTION_URL)

        KeCommand('set_active_client').go().wait()
        KeCommand('reset_errors').go().wait()
        KeCommand('enable_power').go().wait()

        move = KeCommand('path_ptp')
        move.args = {
            'position': {
                'joints': {
                    'main_joints': [0, 0, 120, 0, 0, 0]
                }
            }
        }
        move.go()
        move.args = {
            'position': {
                'joints': {
                    'main_joints': [70, 0, 120, 0, 10, 0]
                }
            }
        }
        move.go()
        KeCommand('start_path_execution').go().wait()

        print('ENDE')
    finally:
        srv.disconnect()
