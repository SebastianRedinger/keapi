import command_server as cs


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

    def go(self) -> cs.Ticket:
        if self.arguments:
            return cs.start(self.name, **self.arguments)
        else:
            return cs.start(self.name)


if __name__ == '__main__':
    COMMAND_CONNECTION_URL = "ws://192.168.71.3:20004/TX2_90/websocket-command"
    try:
        cs.connect_to_socket(COMMAND_CONNECTION_URL)

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
        cs.disconnect_from_socket()
