class KebaError(RuntimeError):
    '''Beschreibt einen Fehler der auf der Steuerung aufgetreten ist'''
    pass


class HttpError(RuntimeError):
    '''
    Beschreibt einen Fehler der durch eine Falsche
    Nutzung aufgetreten ist.
    '''
    pass


class SocketError(RuntimeError):
    '''
    ToDo
    '''
    pass


class TcError(RuntimeError):
    '''
    ToDo
    '''
    pass
