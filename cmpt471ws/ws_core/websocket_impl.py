
import queue

class WebsocketImpl:
    # some default values
    DEFAULT_PORT = 80
    DEFAULT_RCV_BUF_SIZE = 16384
    # role enums
    ROLE_SERVER = "server"
    ROLE_CLIENT = "client"
    # connect state enums
    STATE_NOT_YET_CONNECTED = 100
    STATE_OPEN = 101
    STATE_CLOSING = 102
    STATE_CLOSED = 103

    def __init__(self, listener, role):
        # socket
        self.listener = listener
        # TODO should we have a limit for queue size?
        self.out_queue = queue.Queue()
        self.in_queue = queue.Queue()
        # Client or Server TODO refactor this to use enum
        self.role = role
        # selection key
        self.key = None
        # socket fileobj
        self.wrapped_socket = None
        # executor assigned
        self.executor = None


        # The following attributes are necessary for managing websocket protocol states
        self.ready_state = WebsocketImpl.STATE_NOT_YET_CONNECTED
    def set_key(self, selection_key):
        self.key = selection_key


    def set_wrapped_socket(self, wrapped_socket):
        self.wrapped_socket = wrapped_socket


    def set_executor(self, executor):
        self.executor = executor

    def put_inqueue(self, data):
        self.in_queue.put(data)

    def get_inqueue(self):
        return self.in_queue.get(True, None)

    def put_outqueue(self, data):
        self.out_queue.put(data)

    def get_outqueue(self):
        # TODO should this be blocking ? yes
        return self.out_queue.get(True, None)

    def decode(self, data):
        pass




